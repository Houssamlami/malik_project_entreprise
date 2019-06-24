# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
import string
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    prix_achat = fields.Float(string=u"Prix d\'Achat")
    prix_transport = fields.Float(string=u"Prix de Transport")
    cout_avs = fields.Float(string=u"Coût AVS")
    cout_ttm = fields.Float(string=u"Coût TTM")
    charge_fixe = fields.Float(string=u"Charge Fixe")
    cout_revient = fields.Float(compute='calcul_prix_min_vente_estime', string=u"Prix de revient")
    prix_min_vente = fields.Float(compute='calcul_prix_min_vente', string=u"Prix de vente Min")
    marge = fields.Float(string=u"Marge Commerciale")
    marge_securite = fields.Float(string=u"Marge de securité")
    provision_commission = fields.Float(string="Provision de commission")
    prix_vente_estime = fields.Float(compute='calcul_prix_vente', string=u"Prix de vente Conseillé")
    code_geo = fields.Text(string="Code Geo")
    
    @api.constrains('default_code')
    def _check_default_code(self):
        code = self.search([('default_code','=',self.default_code)])
        if len(code) > 1:
            raise ValidationError(_("Reference interne du produit en double"))
    
    
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','provision_commission')
    def calcul_prix_min_vente_estime(self):
        for record in self:
            if record.prix_achat:
                record.cout_revient = (record.prix_achat + record.prix_transport + record.cout_avs + record.cout_ttm + record.charge_fixe + record.provision_commission)
                
    @api.depends('cout_revient','marge_securite')
    def calcul_prix_min_vente(self):
        for record in self:
            if record.marge_securite:
                record.prix_min_vente = record.cout_revient + record.marge_securite
    
    @api.depends('marge', 'prix_min_vente')
    def calcul_prix_vente(self):
        for record in self:
            if record.marge:
                record.prix_vente_estime = record.prix_min_vente + record.marge
                record.list_price = record.prix_vente_estime
    
    @api.onchange('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat')
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat')
    def onchange_prix(self):
        for record in self:
            record.calcul_prix_min_vente()
            record.calcul_prix_min_vente_estime()
            record.calcul_prix_vente()