# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, exceptions, models, _
import string
from odoo.exceptions import ValidationError
from odoo.exceptions import except_orm, Warning, RedirectWarning
import datetime
import time
from datetime import *
from odoo.tools.misc import formatLang
from odoo.addons import decimal_precision as dp


# Record l androit de stockage genre : sec , frais, volailles ou surgele , ainsi que la position d'affichage sur le bon de preparation
class AndroitStotackage(models.Model):
    _name ="androit.stockage"


    name = fields.Char(string='Endroit de stockage')

class Preparation(models.Model):
    _name ="androit.preparation"


    name = fields.Char(string='Position de prepration')
  
    
class ProductTag(models.Model):
    _description = 'Product Tags'
    _name = "product.tag"

    name = fields.Char('Nom Tag', required=True, translate=True)
    active = fields.Boolean(help='The active field allows you to hide the tag without removing it.', default=True)
    parent_id = fields.Many2one(string='Tag Parent', comodel_name='product.tag', index=True, ondelete='cascade')
    child_ids = fields.One2many(string='Tags fils', comodel_name='product.tag', inverse_name='parent_id')
    parent_left = fields.Integer('Parent gauche', index=True)
    parent_right = fields.Integer('Parent droite', index=True)

    image = fields.Binary('Image')

    # _parent_store = True
    # _parent_order = 'name'
    # _order = 'parent_left'

    @api.multi
    def name_get(self):
        """ Return the tags' display name, including their direct parent. """
        res = {}
        for record in self:
            current = record
            name = current.name
            while current.parent_id:
                name = '%s / %s' % (current.parent_id.name, name)
                current = current.parent_id
            res[record.id] = name

        return  [(record.id,  record.name) for record in self]

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        tags = self.search(args, limit=limit)
        return tags.name_get()

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
                
    @api.depends('prix_vente_estime')
    def _compute_standard_price(self):
        for template in self:
            precision_currency = template.currency_id or template.company_id.currency_id
            if template.number_unit:
                template.standard_price = precision_currency.round(template.number_unit*template.prix_vente_estime)
            elif template.prix_vente_estime:
                value = template.prix_vente_estime
                template.standard_price = value
            else:
                unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
                for templates in unique_variants:
                    templates.standard_price = templates.product_variant_ids.standard_price
                for templates in (self - unique_variants):
                    templates.standard_price = 0.0
                
    @api.one    
    def on_product_state2(self):
        self.ensure_one()
        today = str(datetime.now().date())
        test_on_product_version2 = 0
        test_on_product_version3 = 0
        for record in self:
            record.ensure_one()
            record.test_on_product = record.qty_available
            test_on_product_version3 = self.env['product.product'].search([('product_tmpl_id', '=', record.id)], limit=1).id
            record.test_on_product_version3 = test_on_product_version3
            vouchers = self.env['sale.order'].search([('requested_date', '>', today)])
            productbl = self.env['sale.order.line'].search([
            ('product_id', '=', record.test_on_product_version3.id),('qty_delivered', '=', 0),('order_id', 'in', vouchers.ids)])
            for rec in productbl:
                test_on_product_version2 += rec.product_uom_qty
            record.test_on_product_version2 = test_on_product_version2
            print(record)
            
            print(record.test_on_product_ver)
            if record.weight>0 and record.uom_id.name == 'kg':
                record.test_on_product_ver_colis_for_kg = round((record.test_on_product_ver/record.weight))
        self.test_on_product_ver = self.test_on_product-self.test_on_product_version2
        if self.sale_secondary_uom_id and self.uom_id.name == 'kg':
            factor = self.sale_secondary_uom_id.factor
            if factor != 0:
                self.test_on_product_ver_colis_for_kg = round((self.test_on_product_ver/(factor)))
                self.test_on_product_version2 = round((self.test_on_product_version2/(factor)))
        
#les deux methodes qui fonctionnent pour catalogur --> le stock virtuel :                       
    def calcule_stock_virtuel_actuel(self):
        today = str(datetime.now().date())
        qty_virtuelle_des_comandes=0
        for record in self:
            if record.id:
                #vouchers = self.env['sale.order'].search([('requested_date', '>', today),('state','in',['sale','draft'])])
                vouchers = self.env['sale.order'].search([('requested_date', '>', today),('state','in',['sale', 'draft'])])
                productbl = self.env['sale.order.line'].search([
                ('product_id', '=', self.env['product.product'].search([('product_tmpl_id', '=', record.id)]).id),('qty_delivered', '=', 0),('order_id', 'in', vouchers.ids)])
                for rec in productbl:
                    # if record.qty_available:
                    qty_virtuelle_des_comandes += rec.secondary_uom_qty
                record.qty_virtuelle_des_comandes = qty_virtuelle_des_comandes
                if record.sale_secondary_uom_id and record.uom_id.name == 'kg':
                    factor = record.sale_secondary_uom_id.factor
                    if factor != 0:
                        record.stock_virtuel_actuel = round((record.qty_available-record.qty_virtuelle_des_comandes)/(factor))
                else:
                    record.stock_virtuel_actuel = round((record.qty_available-record.qty_virtuelle_des_comandes)) or 0.00
                    
                if record.sale_secondary_uom_id and record.uom_id.name == 'kg':
                    factor = record.sale_secondary_uom_id.factor
                    if factor != 0:
                        record.qty_available_colis_real_stock = round(record.qty_available/factor)
                else:
                    record.qty_available_colis_real_stock = record.qty_available
                # record.test_on_change_ver = record.test_on_change-record.test_on_change_version2
                # if record.uom_id.id==3:
                    # record.stock_virtuel_actuel = round(((record.qty_available-record.qty_virtuelle_des_comandes)/record.weight)) or 0.00
                # else:
                    # record.stock_virtuel_actuel = round((record.qty_available-record.qty_virtuelle_des_comandes))
    #' @api.depends('id)
    def calcule_nombre_colis_a_livre(self, field_names=None):
        #todayy = datetime.today()
        today = str(datetime.now().date())
        nombre_colis=0
        article=0
        for record in self:
            if record.id:
                article= self.env['product.product'].search([('product_tmpl_id', '=', record.id)])
                #vouchers1 = self.env['sale.order'].search([('state','in',['sale','draft']),('requested_date', '>', (todayy + timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')), ('requested_date', '<', (todayy + timedelta(days=1)).strftime('%Y-%m-%d 23:59:59'))])
                vouchers1 = self.env['sale.order'].search([('requested_date', '>', today),('state','in',['sale', 'draft'])])
                productbl1 = self.env['sale.order.line'].search([
                ('product_id', '=', article.id),('qty_delivered', '=', 0),('order_id', 'in', vouchers1.ids)])
                if len(productbl1)>0:
                    for rec1 in productbl1:
                        nombre_colis += rec1.secondary_uom_qty
                    record.nombre_colis_a_livre = nombre_colis or 0.00
                    record.qty_verti_rest = record.qty_available_colis_real_stock-record.nombre_colis_a_livre or 0.00                      
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
                    
    @api.multi
    @api.depends('tag_ids')
    def _compute_first_tag_id(self):
        for record in self:
            record.first_tag_id = record.tag_ids and record.tag_ids[0] or False


    first_tag_id = fields.Many2one('product.tag', compute=_compute_first_tag_id, store=True)
    Androit_stockage = fields.Many2one(comodel_name='androit.stockage', string="Endroit de stockage", required=True, track_visibility='onchange')
    Androit_preparation = fields.Many2one(comodel_name='androit.preparation', string=u"Endroit de Préparation", required=True, track_visibility='onchange')               
    number_unit = fields.Float(string="Nombre d'unité", track_visibility='onchange')
    name_uom_product = fields.Char(related='uom_id.name', string="Nom Unité de mesure")
    price_cart = fields.Float(string="Prix de vente par piéce à la carte", track_visibility='onchange')
    price_for_calcul = fields.Float(string="Prix de vente pour calcul", track_visibility='onchange')
    prix_achat = fields.Float(string=u"Prix d\'Achat", track_visibility='onchange')
    prix_transport = fields.Float(string=u"Transport Achat", track_visibility='onchange')
    cout_avs = fields.Float(string=u"Certification", track_visibility='onchange')
    cout_ttm = fields.Float(string=u"Transport Vente", track_visibility='onchange')
    price_for_buy = fields.Float(compute='_get_prix_vente_produit')
    charge_fixe = fields.Float(string=u"Charge Fixe", help=u"Ce pourcentage se base sur la somme du Prix d\'Achat, Prix de Transport, Coût AVS et Coût TTM", track_visibility='onchange')
    cout_revient = fields.Float(compute='calcul_prix_min_vente_estime', string=u"Coût de revient de base", track_visibility='onchange')
    prix_min_vente = fields.Float(compute='calcul_prix_min_vente', string=u"Prix de vente Min", track_visibility='onchange')
    marge = fields.Float(string=u"Marge Commerciale", track_visibility='onchange')
    marge_securite = fields.Float(string=u"Marge de securité", track_visibility='onchange')
    provision_commission = fields.Float(string="Provision de commission", track_visibility='onchange')
    prix_vente_estime = fields.Float(compute='calcul_prix_vente', string=u"Prix de vente Conseillé", track_visibility='onchange')
    code_geo = fields.Text(string="Code Geo", track_visibility='onchange')
    sales_count2 = fields.Integer(compute='_sales_count2', string='# Salesss')
    test_on_product = fields.Float('Qte en stock reel', compute='on_product_state2')
    test_on_product_ver = fields.Float('Qte restante virtuell', compute='on_product_state2')
    test_on_product_ver_colis_for_kg = fields.Float('Qte restante virtuell en colis ', compute='on_product_state2')
    test_on_product_version2= fields.Float('Qte a livre apre today',compute='on_product_state2')
    test_on_product_version3= fields.Many2one(comodel_name='product.product', string='Qte a livre apre today3',compute='on_product_state2')
    test_on_product_vertuel_jours_suivant2= fields.Float('max qty disponible en stock le jour j',compute='on_product_vertuel_jours_suivant')
    total_commande_jour_suivant= fields.Float('Qte a livre le jour j+1',compute='on_product_vertuel_jours_suivant')
    stock_virtuel_jour_suivant= fields.Float('Qte en tock virtuel le jour j+1',compute='on_product_vertuel_jours_suivant')
    stock_virtuel_actuel = fields.Float('Qty virtuel actuel' , compute='calcule_stock_virtuel_actuel')
    qty_virtuelle_des_comandes = fields.Float(string="Quantité v des cmd" , compute='calcule_stock_virtuel_actuel')
    qty_available_colis_real_stock = fields.Float(string=u"Quantité en stock" , compute='calcule_stock_virtuel_actuel')
    nombre_colis_a_livre = fields.Float('nobre colis a livrer' , compute='calcule_nombre_colis_a_livre')
    qty_verti_rest = fields.Float('Qté Vir Res' , compute='calcule_nombre_colis_a_livre')
    qty_vertuel_second_unit = fields.Float(string="Qty in second unit", compute='get_qty_vertuel_second_unit')
    secondary_unit_qty_available = fields.Float(string='Second', readonly=True)
    product_service_commercial = fields.Boolean(string='Disponibilté Service Commercial')
    product_at_zero = fields.Boolean(string=u"Article à zéro AN", track_visibility='onchange')
    tag_ids = fields.Many2many(string='Tags',
                               comodel_name='product.tag',
                               relation='product_product_tag_rel',
                               column1='tag_id',
                               column2='product_id')
    

    def get_qty_vertuel_second_unit(self):
        date_today = datetime.today()
        colis = 0
        product = 0
        for record in self:
            if record.id:
                product = self.env['product.product'].search([('product_tmpl_id', '=', record.id)])
                sales = self.env['sale.order'].search([('state','in',['sale']),('requested_date', '>', fields.Date.to_string(date_today))])
                sale_lines = self.env['sale.order.line'].search([('product_id', '=', product.id),('order_id', 'in', sales.ids),('qty_delivered','=',0)])
                if len(sale_lines) > 0:
                    for line in sale_lines:
                        colis += line.secondary_uom_qty
            record.qty_vertuel_second_unit = record.secondary_unit_qty_available - colis 
    
    
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
            'view_id': self.env.ref('app_sale_order.view_sale_order_line_pivot123').id,
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
    
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','provision_commission','price_for_calcul')
    def calcul_prix_min_vente_estime(self):
        for record in self:
            precision_currency = record.currency_id or record.company_id.currency_id
            if record.prix_achat:
                record.cout_revient = precision_currency.round((record.prix_achat + record.prix_transport + record.cout_avs + record.cout_ttm) + (record.price_for_calcul * (record.provision_commission/100))+((record.charge_fixe/100)*record.price_for_calcul))
            record.standard_price = record.prix_vente_estime
                
    @api.depends('cout_revient','marge_securite', 'price_for_calcul')
    def calcul_prix_min_vente(self):
        for record in self:
            precision_currency = record.currency_id or record.company_id.currency_id
            record.prix_min_vente = precision_currency.round(record.cout_revient + (record.price_for_calcul * (record.marge_securite/100)))
    
    @api.depends('marge', 'prix_min_vente', 'price_for_calcul')
    def calcul_prix_vente(self):
        for record in self:
            precision_currency = record.currency_id or record.company_id.currency_id
            if record.prix_min_vente:
                record.prix_vente_estime = precision_currency.round(record.prix_min_vente + (record.price_for_calcul * (record.marge/100)))
    
    @api.onchange('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','price_for_calcul')
    @api.depends('charge_fixe', 'cout_ttm', 'cout_avs', 'prix_transport', 'prix_achat','price_for_calcul')
    def onchange_prix(self):
        for record in self:
            record.calcul_prix_min_vente()
            record.calcul_prix_min_vente_estime()
            record.calcul_prix_vente()