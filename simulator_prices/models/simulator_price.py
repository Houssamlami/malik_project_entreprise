# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, exceptions, models, _, tools
import string
from odoo.exceptions import ValidationError
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
import time
from datetime import *
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp
import itertools
import psycopg2
from odoo.tools import pycompat


class SimulatorPrice(models.Model):
    _name ="simulator.price"
    _rec_name = 'currency_id'
    
    price_cart = fields.Float(string="Prix de vente par piéce sur la carte")
    prix_achat = fields.Float(string=u"Prix d\'Achat")
    prix_transport = fields.Float(string=u"Transport Achat")
    cout_avs = fields.Float(string=u"Certification")
    cout_ttm = fields.Float(string=u"Transport Vente")
    charge_fixe = fields.Float(string=u"Charge Fixe", help=u"Ce pourcentage se base sur la somme du Prix d\'Achat, Prix de Transport, Coût AVS et Coût TTM")
    cout_revient = fields.Float(compute='calcul_prix_min_vente_estime', string=u"Coût de revient de base")
    prix_min_vente = fields.Float(compute='calcul_prix_min_vente', string=u"Prix de vente Min")
    marge = fields.Float(string=u"Marge Commerciale")
    marge_securite = fields.Float(string=u"Marge de securité")
    provision_commission = fields.Float(string="Provision de commission")
    prix_vente_estime = fields.Float(compute='calcul_prix_vente', string=u"Prix de vente Conseillé")
    currency_id = fields.Many2one(
        'res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id)
    
    @api.multi
    def _compute_currency_id(self):
        try:
            main_company = self.sudo().env.ref('base.main_company')
        except ValueError:
            main_company = self.env['res.company'].sudo().search([], limit=1, order="id")
        for template in self:
            template.currency_id = template.company_id.sudo().currency_id.id or main_company.currency_id.id
    
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','provision_commission','price_cart')
    def calcul_prix_min_vente_estime(self):
        for record in self:
            precision_currency = record.currency_id or record.company_id.currency_id
            if record.prix_achat:
                record.cout_revient = precision_currency.round((record.prix_achat + record.prix_transport + record.cout_avs + record.cout_ttm) + (record.price_cart * (record.provision_commission/100))+((record.charge_fixe/100)*record.price_cart))
            record.standard_price = record.prix_vente_estime
                
    @api.depends('cout_revient','marge_securite', 'price_cart')
    def calcul_prix_min_vente(self):
        for record in self:
            precision_currency = record.currency_id or record.company_id.currency_id
            record.prix_min_vente = precision_currency.round(record.cout_revient + (record.price_cart * (record.marge_securite/100)))
    
    @api.depends('marge', 'prix_min_vente', 'price_cart')
    def calcul_prix_vente(self):
        for record in self:
            precision_currency = record.currency_id or record.company_id.currency_id
            if record.prix_min_vente:
                record.prix_vente_estime = precision_currency.round(record.prix_min_vente + (record.price_cart * (record.marge/100)))
    
    @api.onchange('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','price_cart')
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','price_cart')
    def onchange_prix(self):
        for record in self:
            record.calcul_prix_min_vente()
            record.calcul_prix_min_vente_estime()
            record.calcul_prix_vente()