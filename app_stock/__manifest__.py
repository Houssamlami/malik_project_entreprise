# -*- coding: utf-8 -*-

{
    'name': 'App Malik Stock',
    'summary': 'App Malik Stock',
    'version': '11.0.1.0.0',
    'category': 'Stock',
    'website': '',
    'author': 'FHS Solutions',
    'license': 'AGPL-3',
    'depends': [
        'sale',
        'sale_management',
        'stock',
        'sale_stock',
    ],
    'data': [
        'views/stock_picking_views.xml',
    ],
    
    'application': False,
    'installable': True,
}
