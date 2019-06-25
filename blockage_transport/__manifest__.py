# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'blockage transport',
    'version' : '1.0',
    'summary': 'blockage transport par client pour ttm',
    'sequence': 31,
    'license':'LGPL-3',
    'description': """
Ce module permet de bloquer le transport pour les commande faite pour preparation de la tournee
    """,
    'category': 'Generic Modules/Sales',
    'author' : 'FHS IT Solutions Pvt Ltd',
    'depends' : ['sale_management','base'],
    'data': [
         'views/blockage_transport.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
