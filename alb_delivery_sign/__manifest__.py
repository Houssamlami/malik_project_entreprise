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
        'data/mail_activity.xml',
        'views/partner.xml',
        'views/custumer_reception_wizard.xml',
        'views/stock_picking_views.xml',
        'views/config_motif_view.xml',
        'reports/delivery_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}