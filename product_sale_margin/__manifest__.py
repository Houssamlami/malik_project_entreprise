# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Product Sale Margin',
    'version' : '11.1.7.23',
    'summary': 'Product Sale Margin',
    'sequence': 80,
    'license':'LGPL-3',
    'description': """
    Product Sale Margin
    """,
    'category': 'Product',
    'author' : 'FHS Solutions',
    'depends' : ['product','product_margin'],
    'data': [
        'views/product_margin_views.xml',
        'wizard/product_margin_view_wizard.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
