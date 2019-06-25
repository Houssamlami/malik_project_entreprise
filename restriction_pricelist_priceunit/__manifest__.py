# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Restriction pricelist helpser',
    'version' : '11.1.7.23',
    'summary': '',
    'sequence': 80,
    'license':'LGPL-3',
    'description': """
    Add 
    """,
    'category': 'Sale',
    'author' : 'Naj',
    'depends' : ['sale','sale_management'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
