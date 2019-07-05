# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Smart button sales by day for product for helpser',
    'version' : '1.0',
    'summary': 'Smart button sales by day for product for helpser',
    'sequence': 45,
    'license':'LGPL-3',
    'description': """
Smart button sales by day for product for helpser
    """,
    'category': 'Generic Modules/Sales',
    'author' : 'Najlae B',
    'website' : 'http://www.broadtech-innovations.com',
    'images': ['static/description/banner.jpg'],
    'depends' : ['sale_management','sale','app_product_weight_sale'],
    'data': [
        'views/sale_smart_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
