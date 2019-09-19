# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'App Malik Account Invoice',
    'version' : '11.0',
    'summary': 'App Malik Account Invoice',
    'sequence': 70,
    'license':'LGPL-3',
    'description': """
App Malik Account Invoice
    """,
    'category': 'Generic Modules/Sales',
    'author' : 'FHS IT Solutions',
    'depends' : ['sale_management','sale_order_dates','account','sale'],
    'data': [
          'views/account_invoice_views.xml',
          'views/account_payment_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
