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
        'app_sale_order',
    ],
    'data': [
        'views/stock_picking_views.xml',
        'views/stock_order_preparation_report.xml',
        'views/report_br_stock_empty.xml',
        'views/stock_inventory_views.xml',
        'views/preparation_type_produit_pour_affichage.xml',
        'wizard/wizard_colis.xml',
        'views/template_header.xml',
    ],
    
    'application': False,
    'installable': True,
}
