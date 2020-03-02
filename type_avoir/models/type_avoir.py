# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import tools
from odoo import api, fields, models


# ajouter le type d'avoir
class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
	


    type_avoir = fields.Selection([
        ('Qualité de Produit BONA', 'Qualité de Produit BONA'),
        ('Qualité de Produit Crusvi', 'Qualité de Produit Crusvi'),
        ('Qualité de Produit Imex', 'Qualité de Produit Imex'),
        ('Qualité de Produit Atlas negoce', 'Qualité de Produit Atlas negoce'),
        ('Qualité de Produit Nouvelle Atlas', 'Qualité de Produit Nouvelle Atlas'),
        ('Qualité de Produit Tradco', 'Qualité de Produit Tradco'),
        ('Refus de commandes', 'Refus de commandes'),
        ('Manque de produit à la livraison', 'Manque de produit à la livraison'),
        ('Erreur de préparation TTM', 'Erreur de préparation TTM'),
        ('Annulation de facture et refacturation', 'Annulation de facture et refacturation'),
        ('DLC Courte', 'DLC Courte'),
        ('Erreur de saisie', 'Erreur de saisie'),
        ('Gonflement par commercial', 'Gonflement par commercial'),
        ('Erreur sur la remise', 'Erreur sur la remise'),
        ('Erreur sur le prix', 'Erreur sur le prix'),
        ('Geste commercial', 'Geste commercial'),
        ],)