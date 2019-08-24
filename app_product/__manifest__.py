# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'App Malik Product',
    'version' : '11.1.7.23',
    'summary': 'App Malik Product',
    'sequence': 80,
    'license':'LGPL-3',
    'description': """
    App Malik Product
    """,
    'category': 'Product',
    'author' : 'FHS Solutions',
    'depends' : ['purchase','product'],
    'data': [
        'views/product_template_view.xml',
        'views/product_supplierinfo_views.xml',
        'views/product_product_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
