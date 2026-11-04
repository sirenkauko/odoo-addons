# -*- coding: utf-8 -*-
# Copyright 2026 Kauko Sirén
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Sale Quotation Merge (Odoo 20)',
    'version': '20.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Merge multiple draft sales quotations into a single consolidated quotation',
    'description': """
Sale Quotation Merge for Odoo 20
================================
Merge multiple draft quotations (draft / sent) into a single master quotation
directly from the Quotations list view Action menu.

Features:
- Validates that selected quotations are in draft/sent state and belong to the same customer
- Choose which quotation acts as the master target order
- Option to merge identical product lines (sum up quantities) or keep them separate
- Option to cancel or archive source quotations
- Automatically appends customer notes and terms to the target quotation
- Logs references and links in the chatter on both source and target quotations
- Supports Finnish and English
    """,
    'author': 'Kauko Sirén',
    'website': 'https://github.com/sirenkauko/odoo-addons',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/sale_quotation_merge_views.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
