# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, exceptions, models, _
import string
from odoo.exceptions import ValidationError
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
import time
from datetime import *

class ProductTemplate(models.Model):
    _inherit = 'product.template'


#This function calculate Qty available in stock on Colis if uom_id == KG
    @api.multi
    def _get_prix_vente_produit(self):
        if self.prix_vente_estime:
            for record in self:
                value = record.prix_vente_estime
                record.list_price = value
        if self.cout_revient:
            for record in self:
                value = record.cout_revient
                record.standard_price = value
                record.price_for_buy = record.cout_revient
                
    @api.depends('cout_revient')
    def _compute_standard_price(self):
        if self.cout_revient:
            for record in self:
                value = record.cout_revient
                record.standard_price = value
                
           
            
    def on_product_state2(self):
        today = str(datetime.now().date())
        test_on_product_version2 = 0
        test_on_product_version3 = 0
        for record in self:
            if record.id:
                record.test_on_product = record.qty_available
                record.test_on_product_version3 = self.env['product.product'].search([('product_tmpl_id', '=', record.id)],limit=1).id
                vouchers = self.env['sale.order'].search([('requested_date', '>', today)])
                productbl = self.env['sale.order.line'].search([
                ('product_id', '=', record.test_on_product_version3),('qty_delivered', '=', 0),('order_id', 'in', vouchers.ids)])
                for rec in productbl:
                    test_on_product_version2 += rec.product_uom_qty
                record.test_on_product_version2 = test_on_product_version2
                record.test_on_product_ver = record.test_on_product-record.test_on_product_version2
                if record.weight>0 and record.uom_id.id==3:
                        record.test_on_product_ver_colis_for_kg = round((record.test_on_product_ver/record.weight))
                        
                        
#Cette fonction permet de calculer les qte a livrer j+1 (les commande saisie de la jour j) et la qte qui doit rester en stock le jour j                 
                        
    def on_product_vertuel_jours_suivant(self):
        today = datetime.today()
        test_on_product_vertuel_jours_suivant2 = 0
        test_on_product_vertuel_jours_suivant3 = 0
        max_id= 0
        total_commande_jour_suivant= 0
        stock_virtuel_jour_suivant= 0
        for record in self:
            if record.id:
                record.test_on_product_vertuel_jours_suivant3 = self.env['product.product'].search([('product_tmpl_id', '=', record.id)]).id
                vouchers = self.env['sale.order'].search([('requested_date', '>', (today + timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')), ('requested_date', '<', (today + timedelta(days=1)).strftime('%Y-%m-%d 23:59:59'))])
                productbl = self.env['sale.order.line'].search([
                ('product_id', '=', record.test_on_product_vertuel_jours_suivant3),('qty_delivered', '=', 0),('order_id', 'in', vouchers.ids)])
                for rec in productbl:
                    max_id = max(rec).qty_disponible_en_stock
                    total_commande_jour_suivant += rec.product_uom_qty
                if record.weight>0 and record.uom_id.id==3:
                    record.test_on_product_vertuel_jours_suivant2 = round((max_id/record.weight))
                    record.total_commande_jour_suivant = round((total_commande_jour_suivant/record.weight))
                    record.stock_virtuel_jour_suivant = record.test_on_product_vertuel_jours_suivant2 - record.total_commande_jour_suivant
                else :
                    record.test_on_product_vertuel_jours_suivant2 = max_id
                    record.total_commande_jour_suivant = total_commande_jour_suivant
                    record.stock_virtuel_jour_suivant = record.test_on_product_vertuel_jours_suivant2 - record.total_commande_jour_suivant
                    
              
    prix_achat = fields.Float(string=u"Prix d\'Achat")
    prix_transport = fields.Float(string=u"Prix de Transport")
    cout_avs = fields.Float(string=u"Coût AVS")
    cout_ttm = fields.Float(string=u"Coût TTM")
    price_for_buy = fields.Float(compute='_get_prix_vente_produit')
    charge_fixe = fields.Float(string=u"Charge Fixe", help=u"Ce pourcentage se base sur la somme du Prix d\'Achat, Prix de Transport, Coût AVS et Coût TTM")
    cout_revient = fields.Float(compute='calcul_prix_min_vente_estime', string=u"Prix de revient")
    prix_min_vente = fields.Float(compute='calcul_prix_min_vente', string=u"Prix de vente Min")
    marge = fields.Float(string=u"Marge Commerciale")
    marge_securite = fields.Float(string=u"Marge de securité")
    provision_commission = fields.Float(string="Provision de commission")
    prix_vente_estime = fields.Float(compute='calcul_prix_vente', string=u"Prix de vente Conseillé")
    code_geo = fields.Text(string="Code Geo")
    sales_count2 = fields.Integer(compute='_sales_count2', string='# Salesss')
    test_on_product = fields.Float('Qte en tock reel', compute='on_product_state2')
    test_on_product_ver = fields.Float('Qte restante virtuell', compute='on_product_state2')
    test_on_product_ver_colis_for_kg = fields.Float('Qte restante virtuell en colis ', compute='on_product_state2')
    test_on_product_version2= fields.Float('Qte a livre apre today',compute='on_product_state2')
    test_on_product_version3= fields.Integer('Qte a livre apre today3',compute='on_product_state2')
    test_on_product_vertuel_jours_suivant2= fields.Float('max qty disponible en stock le jour j',compute='on_product_vertuel_jours_suivant')
    total_commande_jour_suivant= fields.Float('Qte a livre le jour j+1',compute='on_product_vertuel_jours_suivant')
    stock_virtuel_jour_suivant= fields.Float('Qte en tock virtuel le jour j+1',compute='on_product_vertuel_jours_suivant')
    
    
    #''''''''''''''''''''''''Smart button sales by day for product for helpser''''''''''''''''''''''''''''''''''''''''
    
    @api.multi
    @api.depends('product_variant_ids.sales_count2')
    def _sales_count2(self):
        for product in self:
            product.sales_count2 = sum([p.sales_count2 for p in product.with_context(active_test=False).product_variant_ids])

    @api.multi
    def action_view_saless(self):
        self.ensure_one()
        action = self.env.ref('app_sale_order.action_product_sale_list34')
        product_ids = self.with_context(active_test=False).product_variant_ids.ids

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('product_id.product_tmpl_id', '=', self.id)],
        }
    #'''''''''''''''''''''''uniqueness of the product reference'''''''''''''''''''''''''''''''''''''''''''''''
    
    @api.onchange('default_code')
    def onchange_default_code_product(self):
        for product in self:
            if product.default_code :
                prod = self.env['product.template'].search([
                ('default_code', 'like', product.default_code)], limit=1)
                if prod.default_code == product.default_code:
                    raise exceptions.ValidationError(_('Reference interne du produit en double !'))
                    return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                    }

    
    
    #'''''''''''''''''''''''calculate costs/prices of product'''''''''''''''''''''''''''''''''''''''''''''''''''''
    
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','provision_commission')
    def calcul_prix_min_vente_estime(self):
        for record in self:
            if record.prix_achat:
                record.cout_revient = ((record.prix_achat + record.prix_transport + record.cout_avs + record.cout_ttm) * (1 +(record.charge_fixe/100)) + record.provision_commission)
            record.standard_price = record.cout_revient
                
    @api.depends('cout_revient','marge_securite')
    def calcul_prix_min_vente(self):
        for record in self:
            if record.marge_securite:
                record.prix_min_vente = record.cout_revient *(1 + (record.marge_securite/100))
    
    @api.depends('marge', 'prix_min_vente')
    def calcul_prix_vente(self):
        for record in self:
            if record.prix_min_vente:
                record.prix_vente_estime = record.prix_min_vente + record.marge
            record.list_price = record.prix_vente_estime
    
    @api.onchange('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat')
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat')
    def onchange_prix(self):
        for record in self:
            record.calcul_prix_min_vente()
            record.calcul_prix_min_vente_estime()
            record.calcul_prix_vente()