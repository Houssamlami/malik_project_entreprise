# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'type_avoir',
    'version' : '11.0',
    'summary': 'type_avoir',
    'sequence': 93,
    'license':'LGPL-3',
    'description': """
Add the invoice type on the out invoice
    """,
    'category': 'Generic Modules/type_avoir',
    'author' : 'Naj',
    'depends' : ['account'],
    'data': [
        'views/type_avoir.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
