# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'teste on change',
    'version' : '1.0',
    'summary': 'teste on change',
    'sequence': 76,
    'license':'LGPL-3',
    'description': """
teste_on_change
    """,
    'category': 'Generic Modules/Sales',
    'author' : 'FHS IT Solutions Pvt Ltd',
    'images': ['static/description/banner.jpg'],
    'depends' : ['sale_management'],
    'data': [
          'views/sale_stock_availability.xml',
          'views/etat_stock_virtuel_un_jours_apres_commande.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
