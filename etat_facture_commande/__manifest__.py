# -*- coding: utf-8 ---*---
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Etat de facture pour commande',
    'version' : '1.0',
    'summary': 'Etat de la facture pour les commandes',
    'sequence': 39,
    'license':'LGPL-3',
    'description': """
Verification de l etat de la facture dans une commande , soit entierement facture ,partiellement facture ou a facturer
    """,
    'category': 'Generic Modules/Sales',
    'author' : 'FHS IT Solutions Pvt Ltd',
    'depends' : ['sale_management'],
    'data': [
        'views/etat_facture_commande.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
