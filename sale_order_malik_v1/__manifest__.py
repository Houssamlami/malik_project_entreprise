# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'sale order helpser',
    'version' : '11.1.7.23',
    'summary': 'sale order helpser',
    'sequence': 80,
    'license':'LGPL-3',
    'description': """
    Add 
    """,
    'category': 'Sale',
    'depends' : ['sale'],
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