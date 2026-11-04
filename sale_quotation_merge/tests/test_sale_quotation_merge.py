# -*- coding: utf-8 -*-
# Copyright 2026 Kauko Sirén
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestSaleQuotationMerge(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_a = cls.env['res.partner'].create({'name': 'Asiakas A Oy'})
        cls.partner_b = cls.env['res.partner'].create({'name': 'Asiakas B Oy'})

        cls.product_1 = cls.env['product.product'].create({
            'name': 'Testituote 1',
            'type': 'consu',
            'list_price': 100.0,
        })
        cls.product_2 = cls.env['product.product'].create({
            'name': 'Testituote 2',
            'type': 'consu',
            'list_price': 50.0,
        })

    def _create_order(self, partner, lines, note=None):
        order_line_vals = []
        for prod, qty, price in lines:
            order_line_vals.append((0, 0, {
                'product_id': prod.id,
                'product_uom_qty': qty,
                'price_unit': price,
            }))
        return self.env['sale.order'].create({
            'partner_id': partner.id,
            'note': note or '',
            'order_line': order_line_vals,
        })

    def test_merge_two_quotations_separate_lines(self):
        """Yhdistää kaksi eri tuotetta sisältävää tarjousta siten, että molemmat rivit jäävät erillisiksi."""
        so1 = self._create_order(self.partner_a, [(self.product_1, 2, 100.0)], note="Ehto 1")
        so2 = self._create_order(self.partner_a, [(self.product_2, 3, 50.0)], note="Ehto 2")

        wizard = self.env['sale.quotation.merge'].with_context(
            active_ids=[so1.id, so2.id],
            active_model='sale.order',
        ).create({
            'merge_lines': False,
            'keep_notes': True,
            'action_source_orders': 'cancel',
        })

        wizard.action_merge()

        # Kohdetarjouksella tulee olla 2 riviä
        self.assertEqual(len(so1.order_line), 2)
        prod1_line = so1.order_line.filtered(lambda l: l.product_id == self.product_1)
        prod2_line = so1.order_line.filtered(lambda l: l.product_id == self.product_2)
        self.assertEqual(prod1_line.product_uom_qty, 2)
        self.assertEqual(prod2_line.product_uom_qty, 3)

        # Lähdetarjous on peruttu
        self.assertEqual(so2.state, 'cancel')

        # Muistiinpanot yhdistetty
        self.assertIn("Ehto 1", so1.note)
        self.assertIn("Ehto 2", so1.note)

    def test_merge_two_quotations_merge_same_lines(self):
        """Yhdistää kaksi tarjousta, joissa on sama tuote ja hinta, summattuna yhdelle riville."""
        so1 = self._create_order(self.partner_a, [(self.product_1, 2, 100.0)])
        so2 = self._create_order(self.partner_a, [(self.product_1, 5, 100.0)])

        wizard = self.env['sale.quotation.merge'].with_context(
            active_ids=[so1.id, so2.id],
            active_model='sale.order',
        ).create({
            'target_order_id': so1.id,
            'merge_lines': True,
            'action_source_orders': 'cancel',
        })

        wizard.action_merge()

        # Tuotteen 1 määrä tulisi olla 2 + 5 = 7 yhdellä rivillä
        self.assertEqual(len(so1.order_line), 1)
        self.assertEqual(so1.order_line.product_uom_qty, 7.0)
        self.assertEqual(so2.state, 'cancel')

    def test_merge_validation_errors(self):
        """Testaa virhetarkistukset: liian vähän tarjouksia, eri asiakas, ei-luonnostila."""
        so1 = self._create_order(self.partner_a, [(self.product_1, 1, 100.0)])
        so_b = self._create_order(self.partner_b, [(self.product_1, 1, 100.0)])

        # Alle kaksi tarjousta
        with self.assertRaises(UserError):
            self.env['sale.quotation.merge'].with_context(active_ids=[so1.id]).default_get([])

        # Eri asiakkaat
        with self.assertRaises(UserError):
            self.env['sale.quotation.merge'].with_context(active_ids=[so1.id, so_b.id]).default_get([])

        # Tilaus ei ole luonnostilassa (vahvistetaan so1)
        so2 = self._create_order(self.partner_a, [(self.product_1, 1, 100.0)])
        so1.action_confirm()
        with self.assertRaises(UserError):
            self.env['sale.quotation.merge'].with_context(active_ids=[so1.id, so2.id]).default_get([])
