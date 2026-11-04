# -*- coding: utf-8 -*-
# Copyright 2026 Kauko Sirén
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleQuotationMerge(models.TransientModel):
    _name = 'sale.quotation.merge'
    _description = 'Merge Quotations'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        orders = self.env['sale.order'].browse(active_ids)

        if len(orders) < 2:
            raise UserError(_("Please select at least two quotations to merge."))

        invalid_orders = orders.filtered(lambda o: o.state not in ('draft', 'sent'))
        if invalid_orders:
            invalid_names = ", ".join(invalid_orders.mapped('name'))
            raise UserError(
                _("Only quotations in draft or sent state can be merged. "
                  "The following orders are not in draft: %s.") % invalid_names
            )

        commercial_partners = orders.mapped('partner_id.commercial_partner_id')
        if len(commercial_partners) > 1:
            raise UserError(_("All selected quotations must belong to the same customer."))

        companies = orders.mapped('company_id')
        if len(companies) > 1:
            raise UserError(_("All selected quotations must belong to the same company."))

        currencies = orders.mapped('currency_id')
        if len(currencies) > 1:
            raise UserError(_("All selected quotations must have the same currency."))

        res['order_ids'] = [(6, 0, orders.ids)]
        res['target_order_id'] = orders[0].id
        return res

    order_ids = fields.Many2many(
        'sale.order',
        string="Quotations to Merge",
        required=True,
    )
    target_order_id = fields.Many2one(
        'sale.order',
        string="Target Quotation",
        required=True,
        domain="[('id', 'in', order_ids)]",
        help="Quotation into which lines from other quotations will be merged.",
    )
    merge_lines = fields.Boolean(
        string="Consolidate Identical Lines",
        default=False,
        help="Combine quantities for lines sharing the same product, unit price, discount, and taxes.",
    )
    keep_notes = fields.Boolean(
        string="Keep Terms and Notes",
        default=True,
        help="Append terms and notes from source quotations to the target quotation.",
    )
    action_source_orders = fields.Selection(
        [
            ('cancel', 'Cancel source quotations (Recommended)'),
            ('archive', 'Archive source quotations'),
            ('none', 'Do not modify source quotations'),
        ],
        string="Source Quotations Action",
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
            raise UserError(_("No source quotations to merge."))

        for source in source_orders:
            for line in source.order_line:
                if self.merge_lines and not line.display_type and line.product_id:
                    matched_line = self._find_matching_target_line(line, target.order_line)
                    if matched_line:
                        matched_line.product_uom_qty += line.product_uom_qty
                        continue

                line.copy({
                    'order_id': target.id,
                })

            if self.keep_notes and source.note:
                note_entry = f"[{source.name}]: {source.note}"
                if target.note:
                    target.note = f"{target.note}\n\n{note_entry}"
                else:
                    target.note = note_entry

            source.message_post(
                body=_("Quotation merged into <a href='#' data-oe-model='sale.order' data-oe-id='%(target_id)s'>%(target_name)s</a>.",
                       target_id=target.id, target_name=target.name)
            )

            if self.action_source_orders == 'cancel':
                source.action_cancel()
            elif self.action_source_orders == 'archive':
                if 'active' in source._fields:
                    source.write({'active': False})
                else:
                    source.action_cancel()

        source_links = ", ".join([
            f"<a href='#' data-oe-model='sale.order' data-oe-id='{s.id}'>{s.name}</a>"
            for s in source_orders
        ])
        target.message_post(
            body=_("The following quotations were merged into this quotation: %(source_links)s.",
                   source_links=source_links)
        )

        return {
            'type': 'ir.actions.act_window',
            'name': target.name,
            'res_model': 'sale.order',
            'res_id': target.id,
            'view_mode': 'form',
            'target': 'current',
        }
