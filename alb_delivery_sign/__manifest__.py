# -*- coding: utf-8 -*-
{
    'name': "Delivery Sign",

    'summary': """
        Delivery Sign
    """,

    'description': """
        
    """,

    'author': "LABIBI Ayoub",
    'website': "http://www.yourcompany.com",


    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','web_widget_digitized_signature','stock_barcode'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/partner.xml',
        'views/custumer_reception_wizard.xml',
        'views/stock_picking_views.xml',
        'reports/delivery_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}