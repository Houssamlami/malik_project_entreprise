# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'credit on change',
    'version' : '1.0',
    'summary': 'credit on change',
    'sequence': 77,
    'license':'LGPL-3',
    'description': """
teste_on_change
    """,
    'category': 'Generic Modules/Sales',
    'author' : 'FHS IT Solutions Pvt Ltd',
    'depends' : ['sale_management','app_commercial_vendeur_equipevente','sale_order_dates','account','sale'],
    'data': [
          'views/credit_on_change.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
