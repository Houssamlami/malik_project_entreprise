# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'App Malik Sales Order',
    'version' : '11.1.7.30',
    'summary': 'App Malik Sales Order',
    'sequence': 10,
    'license':'LGPL-3',
    'description': """
    App Malik Sales Order
    """,
    'category': 'Sale',
    'author' : 'FHS Solutions',
    'website' : '',
    'images': ['static/description/banner.jpg'],
    'depends' : ['sale_management', 'sale', 'sale_order_dates', 'sales_team','product','base'],
    'data': [
        'views/group_views.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/sale_order_line_views.xml',
        'views/portal_template.xml'
        
        
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
