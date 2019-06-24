# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Add & compute prices of product',
    'version' : '11.1.7.23',
    'summary': 'Add & compute prices of product',
    'sequence': 80,
    'license':'LGPL-3',
    'description': """
    Add 
    """,
    'category': 'Purchase',
    'author' : 'FHS Solutions',
    'depends' : ['purchase','product'],
    'data': [
        'views/product_template_view.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
