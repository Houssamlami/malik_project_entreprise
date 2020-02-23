# -*- coding: utf-8 -*-


{
    'name': u'MV Relevé Client',
    'version': '11.0',
    'category': 'Reporting',
    'sequence': 1,
    'summary': '',
    'description': """

""",
    'author': ' FHS Solutions',
    'website' : '',
    'depends': ['base','product','account','web',],
    'data': [
             'wizard/statment_customer_wizard_view.xml',
             'report/statment_customer_template.xml',
             ],
    'demo': [
    ],
    'test': [
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
}