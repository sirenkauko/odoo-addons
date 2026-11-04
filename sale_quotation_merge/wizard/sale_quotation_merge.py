# -*- coding: utf-8 -*-
# Copyright 2026 Kauko Sirén
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class SaleQuotationMerge(models.TransientModel):
    _name = 'sale.quotation.merge'
    _description = 'Yhdistä tarjoukset'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        orders = self.env['sale.order'].browse(active_ids)

        if len(orders) < 2:
            raise UserError("Valitse vähintään kaksi tarjousta yhdistettäväksi.")

        invalid_orders = orders.filtered(lambda o: o.state not in ('draft', 'sent'))
        if invalid_orders:
            invalid_names = ", ".join(invalid_orders.mapped('name'))
            raise UserError(
                f"Vain luonnostilassa (Tarjous / Tarjous lähetetty) olevia tarjouksia voi yhdistää. "
                f"Seuraavat tilaukset eivät ole luonnostilassa: {invalid_names}."
            )

        commercial_partners = orders.mapped('partner_id.commercial_partner_id')
        if len(commercial_partners) > 1:
            raise UserError("Kaikkien yhdistettävien tarjousten täytyy kuulua samalle asiakkaalle.")

        companies = orders.mapped('company_id')
        if len(companies) > 1:
            raise UserError("Kaikkien yhdistettävien tarjousten täytyy kuulua samalle yritykselle.")

        currencies = orders.mapped('currency_id')
        if len(currencies) > 1:
            raise UserError("Kaikkien yhdistettävien tarjousten valuutan täytyy olla sama.")

        res['order_ids'] = [(6, 0, orders.ids)]
        res['target_order_id'] = orders[0].id
        return res

    order_ids = fields.Many2many(
        'sale.order',
        string="Yhdistettävät tarjoukset",
        required=True,
    )
    target_order_id = fields.Many2one(
        'sale.order',
        string="Kohdetarjous",
        required=True,
        domain="[('id', 'in', order_ids)]",
        help="Tarjous, johon muiden tarjousten rivit yhdistetään.",
    )
    merge_lines = fields.Boolean(
        string="Yhdistä samat tuoterivit",
        default=False,
        help="Laskee määrät yhteen riveille, joilla on sama tuote, yksikköhinta, alennus ja verot.",
    )
    keep_notes = fields.Boolean(
        string="Kopioi myös ehdot ja muistiinpanot",
        default=True,
        help="Liittää lähdetarjousten ehdot/muistiinpanot kohdetarjouksen lisätietoihin.",
    )
    action_source_orders = fields.Selection(
        [
            ('cancel', 'Peruuta lähdetarjoukset (Suositeltu)'),
            ('archive', 'Arkistoi lähdetarjoukset'),
            ('none', 'Älä muuta lähdetarjouksia'),
        ],
        string="Lähdetarjousten käsittely",
        default='cancel',
        required=True,
    )

    def _get_line_uom(self, line):
        return getattr(line, 'product_uom_id', False) or getattr(line, 'product_uom', False)

    def _get_line_taxes(self, line):
        taxes = getattr(line, 'tax_ids', False)
        if taxes is False:
            taxes = getattr(line, 'tax_id', False)
        return taxes

    def _find_matching_target_line(self, line, target_lines):
        """Etsii kohdetarjoukselta täsmälleen samanlaisen rivin määrän yhdistämistä varten."""
        line_uom = self._get_line_uom(line)
        line_taxes = self._get_line_taxes(line)

        for target_line in target_lines:
            if target_line.display_type:
                continue
            if target_line.product_id != line.product_id:
                continue
            if target_line.price_unit != line.price_unit:
                continue
            if target_line.discount != line.discount:
                continue
            if self._get_line_uom(target_line) != line_uom:
                continue
            if self._get_line_taxes(target_line) != line_taxes:
                continue
            return target_line
        return False

    def action_merge(self):
        self.ensure_one()
        orders = self.order_ids
        target = self.target_order_id
        source_orders = orders - target

        if not source_orders:
            raise UserError("Ei lähdetarjouksia yhdistettäväksi.")

        for source in source_orders:
            for line in source.order_line:
                if self.merge_lines and not line.display_type and line.product_id:
                    matched_line = self._find_matching_target_line(line, target.order_line)
                    if matched_line:
                        matched_line.product_uom_qty += line.product_uom_qty
                        continue

                # Kopioidaan rivi kohdetarjoukselle sellaisenaan
                line.copy({
                    'order_id': target.id,
                })

            # Lisätään muistiinpanot kohdetarjoukseen
            if self.keep_notes and source.note:
                note_entry = f"[{source.name}]: {source.note}"
                if target.note:
                    target.note = f"{target.note}\n\n{note_entry}"
                else:
                    target.note = note_entry

            # Kirjataan lähdetarjouksen chatteriin tieto yhdistämisestä
            source.message_post(
                body=f"Tarjous yhdistetty tarjoukseen <a href='#' data-oe-model='sale.order' data-oe-id='{target.id}'>{target.name}</a>."
            )

            # Käsitellään lähdetarjous
            if self.action_source_orders == 'cancel':
                source.action_cancel()
            elif self.action_source_orders == 'archive':
                if 'active' in source._fields:
                    source.write({'active': False})
                else:
                    source.action_cancel()

        # Kirjataan kohdetarjouksen chatteriin kooste yhdistetyistä tarjouksista
        source_links = ", ".join([
            f"<a href='#' data-oe-model='sale.order' data-oe-id='{s.id}'>{s.name}</a>"
            for s in source_orders
        ])
        target.message_post(
            body=f"Tähän tarjoukseen yhdistettiin seuraavat tarjoukset: {source_links}."
        )

        return {
            'type': 'ir.actions.act_window',
            'name': target.name,
            'res_model': 'sale.order',
            'res_id': target.id,
            'view_mode': 'form',
            'target': 'current',
        }
