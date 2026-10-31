# -*- coding: utf-8 -*-
# Copyright 2026 Kauko Sirén
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    'name': 'Chatter Toggle (Odoo 20)',
    'version': '20.0.1.0.4',
    'category': 'Productivity',
    'summary': 'Toggle button to show or hide the chatter panel in form views',
    'description': """
Chatter Toggle for Odoo 20
==========================
Adds a toggle button to show/hide the chatter sidebar in form views.
When hidden, the form view expands to 100% width, giving maximum space
for order lines, stock picking operations, and data tables.
The toggle state is saved in localStorage.
Supports English and Finnish translations.
    """,
    'author': 'Kauko Sirén',
    'website': 'https://github.com/sirenkauko/odoo-addons',
    'license': 'LGPL-3',
    'depends': ['web', 'mail'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'chatter_toggle/static/src/components/chatter_toggle/chatter_toggle.js',
            'chatter_toggle/static/src/components/chatter_toggle/chatter_toggle.xml',
            'chatter_toggle/static/src/components/chatter_toggle/chatter_toggle.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
