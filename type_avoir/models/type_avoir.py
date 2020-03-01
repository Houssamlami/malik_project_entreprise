# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import tools
from odoo import api, fields, models


# ajouter le type d'avoir
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
	


    type_avoir = fields.Selection([
        ('Qualité de Produit BONA', 'Qualité de Produit Crusvi'),
        ('Qualité de Produit Imex', 'Qualité de Produit Atlas negoce'),
        ('Qualité de Produit Nouvelle Atlas', 'Qualité de Produit Tradco'),
        ('Refus de commandes', 'Manque de produit à la livraison'),
        ('Erreur de préparation TTM', 'Annulation de facture et refacturation'),
        ('DLC Courte', 'Erreur de saisie'),
        ('Gonflement par commercial', 'Erreur sur la remise'),
        ('Erreur sur le prix', 'Geste commercial'),
        ],)