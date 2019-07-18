# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, exceptions, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_weight = fields.Float(string='Total Weight(kg)', compute='_compute_weight_total')
    total_colis = fields.Float(string='Total colis', compute='_compute_colis_total')
    total_volume_ht = fields.Float(string='Montant Total TTC', compute='_compute_volumeht_total')
    total_ht = fields.Float(string='Montant Total HT', compute='_compute_ht_total')
    vendeur = fields.Many2one(comodel_name='res.partner', string="Vendeur")
    user_id = fields.Many2one(comodel_name='res.users', string="Commercial")
    Bolocagettm = fields.Integer('blo')
    Bolocagettm_id = fields.Many2one(comodel_name='blockage.blockage')
    total_weight_stock_char = fields.Float(string='Total charcuterie)', compute='_compute_weight_total_stock_char')
    total_weight_stock_srg = fields.Float(string='Total surgele)', compute='_compute_weight_total_stock_srg')
    total_weight_stock_vv = fields.Float(string='Total volaille)', compute='_compute_weight_total_stock_vv')
    produitalivrer = fields.Char('Produit a livrer', compute='get_product_ttm', store=True)
    Expediteur =  fields.Selection([('MV', 'Malik V'), ('An', 'Atlas N')])    
    zip_df =  fields.Char(string='CP', compute='get_default_zip')
    adresse_liv =  fields.Char(string='Adresse livraison', compute='get_default_zip')
    city =  fields.Char(string='Ville', compute='get_default_zip')    
    observation =  fields.Char(string='Observation')
    test_bloque = fields.Char('Test bloque')
    fac_charcuterie_volaille = fields.Selection([('charcuterie', 'Charcuterie'),('volaille', 'Volaille')],string="Type de commande")
    client_gc_pc = fields.Selection('Type Client', related='partner_id.client_gc_pc', store=True)
    #ecart_qty_kg = fields.Float(string='Ecart qty (KG)', compute='_get_ecart_qty', readonly=True, store=True)
    #ecart_qty_colis = fields.Float('Ecart qty (Colis)', compute=_get_ecart_qty, store=True)
    total_qty_ordred1 = fields.Float(string='Total qtyor', compute='_compute_colis_total_ordred')
    total_qty_delivred = fields.Float(string='Total delievred', compute='_compute_colis_total_delivred')
    total_qty_invoiced = fields.Float(string='Total invoiced', compute='_compute_colis_total_invoiced')
    etat_fac1 = fields.Char(string='Etat facture', compute='_compute_colis_total_etat')
    etat_fac1_copy = fields.Char(string='Etat facture copy', compute='_compute_colis_total_etat_copy',store=True)
    grand_compte = fields.Boolean(string='Commande Grand Compte', default= False)
    
    
    @api.multi
    def compute_qty_transport(self):
        for line in self:
            object = self.env['sale.order.line']
            product = self.env['product.template'].search([('name', '=', 'TRANSPORT GRAND COMPTE')])
            productorigine = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
            dict = 0
            p = self.env['sale.order.line'].search([('product_id', '=', productorigine.id),('order_id','=',line.id)])
            if len(p) == 0:
                for lines in line.order_line:
                    if lines.product_id:
                        dict += lines.product_uom_qty
                object_create = object.create({
                'product_id': productorigine.id,
                'product_uom_qty': dict,
                'qty_delivered':dict,
                'product_uom': product.uom_id.id,
                'order_id':line.id,
                'name':product.name,
                'price_unit':product.list_price,
                'volume_tot':dict*productorigine.list_price
                })
            else:
                dict = 0
                product_already_exist = self.env['sale.order.line'].search([('product_id', '=', productorigine.id),('order_id','=',line.id)])
                for lines in line.order_line:
                    if lines.product_id and (lines.product_id.name != 'TRANSPORT GRAND COMPTE'):
                        dict += lines.product_uom_qty
                object_create = product_already_exist.write({
                'product_id': productorigine.id,
                'product_uom_qty': dict,
                'qty_delivered':dict,
                'product_uom': product.uom_id.id,
                'order_id':line.id,
                'name': product.name,
                'price_unit':product.list_price,
                'volume_tot':dict*productorigine.list_price
                })
    
    
    def _compute_colis_total_ordred(self):
        for sale in self:
            total_qty_ordred1 = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_ordred1 += line.product_uom_qty or 0.0
            sale.total_qty_ordred1 = total_qty_ordred1

    def _compute_colis_total_delivred(self):
        for sale in self:
            total_qty_delivred = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_delivred += line.qty_delivered or 0.0
            sale.total_qty_delivred = total_qty_delivred

    def _compute_colis_total_invoiced(self):
        for sale in self:
            total_qty_invoiced = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_invoiced += line.qty_invoiced or 0.0
            sale.total_qty_invoiced = total_qty_invoiced

    def _compute_colis_total_etat(self):
        for sale in self:
            if sale.total_qty_invoiced == 0:
                sale.etat_fac1 = "A facturer"
            if sale.total_qty_invoiced > 0 :
                sale.etat_fac1 = "facturé"
                
    @api.depends('order_line.qty_invoiced','state')                
    def _compute_colis_total_etat_copy(self):
        for sale in self:
            if sale.total_qty_invoiced == 0:
                sale.etat_fac1_copy = "A facturer"
            if sale.total_qty_invoiced > 0 :
                sale.etat_fac1_copy = "Facturée"
            if sale.state == "cancel":
                sale.etat_fac1_copy = "Annulée"

    @api.onchange('partner_id')
    def on_change_statecr(self):
        for record in self:
            if record.partner_id.bloque:
                record.test_bloque="bloquer"
                raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
                }

    @api.onchange('product_id')
    def on_change_stateproduct(self):
        for record in self:
            if not record.fac_charcuterie_volaille:
                raise exceptions.ValidationError(_('Merci de Choisir le type de votre vente !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
                }
                
    
    @api.multi
    def _prepare_invoice(self):
        
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'date_commande': self.date_order,
            'date_livraison': self.requested_date,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            
        }
        return invoice_vals

    def _compute_weight_total(self):
        for sale in self:
            weight_tot = 0
            for line in sale.order_line:
                if line.product_id:
                    weight_tot += line.weight or 0.0
            sale.total_weight = weight_tot

    def _compute_colis_total(self):
        for sale in self:
            total_colis = 0
            for line in sale.order_line:
                if line.product_id:
                    total_colis += line.product_uom_qty or 0.0
            sale.total_colis = total_colis

    def _compute_volumeht_total(self):
        for sale in self:
            total_volum_ht = 0
            for line in sale.order_line:
                if line.product_id:
                    total_volum_ht += (line.volume_tot * (line.tax_id.amount/100))+line.volume_tot or 0.0
            sale.total_volume_ht = total_volum_ht

    def _compute_ht_total(self):
        for sale in self:
            total_ht = 0
            for line in sale.order_line:
                if line.product_id:
                    total_ht += line.volume_tot or 0.0
            sale.total_ht = total_ht
            

    @api.onchange('partner_id')
    def onchange_get_default_ven(self):
        for partners in self:
            team = 0
            vendeur = 0
            user_id = 0
            if partners.partner_id :
                team=partners.partner_id.id
                productbl = self.env['res.partner'].search([
                ('id', '=', team)])
                vendeur = productbl.vendeur
                user_id = productbl.user_id
            partners.vendeur = vendeur
            partners.user_id = user_id
            # partners.user_id=vendeur_commarcial
            
    @api.multi    
    @api.onchange('partner_id')
    def get_default(self):
        for sales in self:
            Bolocagettm = 0
            if sales.partner_id :
                productbl = self.env['res.partner'].search([
                ('id', '=', sales.partner_id.id)])
                Bolocagettm = productbl.Bolocagettm.id
            sales.Bolocagettm = Bolocagettm
            sales.Bolocagettm_id = Bolocagettm
            
            
    @api.one    
    @api.depends('partner_id')
    def get_default_zip(self):
        for sales in self:
            zip_df = ""
            adresse_liv = ""
            city = ""
            if sales.partner_id :
                productblzip = self.env['res.partner'].search([
                ('id', '=', sales.partner_id.id)])
                zip_df = productblzip.zip
                adresse_liv = productblzip.street
                city = productblzip.city
            sales.zip_df=zip_df
            sales.adresse_liv=adresse_liv
            sales.city=city                        
            
    def _compute_weight_total_stock_char(self):
        for sales in self:
            weight_stock_char = 0
            for line in sales.order_line:
                if line.product_id.categ_id.parent_id.name in ("Sauces","Chips","Saucissons","Chapelet","Mortadelle","Blocs","Panes","Tranches"):
                    weight_stock_char += line.product_uom_qty  or 0.0
            sales.total_weight_stock_char = weight_stock_char
            
    def _compute_weight_total_stock_srg(self):
        for sales in self:
            weight_stock_srg = 0
            for line in sales.order_line:
                if line.product_id.categ_id.parent_id.name in ("Surgeles","IQF"):
                    weight_stock_srg += line.product_uom_qty  or 0.0
            sales.total_weight_stock_srg = weight_stock_srg
            
    def _compute_weight_total_stock_vv(self):
        for sales in self:
            weight_stock_vv = 0
            for line in sales.order_line:
                if line.product_id.categ_id.parent_id.name in ("Volaille","Volailles Espagne","La Volailles BON","Volailles IMEX"):
                    weight_stock_vv += line.product_uom_qty  or 0.0
            sales.total_weight_stock_vv = weight_stock_vv
                    
    
    @api.depends('total_weight_stock_char','total_weight_stock_srg','total_weight_stock_vv')
    def get_product_ttm(self):
        for sales in self:
            if  sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0 and sales.total_weight_stock_srg != 0:
                sales.produitalivrer="Charc + Surg"
            if  sales.total_weight_stock_vv == sales.total_weight_stock_char == 0 and sales.total_weight_stock_srg != 0:
                sales.produitalivrer=" Surg"
            if sales.total_weight_stock_srg == 0 and sales.total_weight_stock_char != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="Charc + VV"
            if  sales.total_weight_stock_srg == sales.total_weight_stock_char == 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer=" VV"
            if sales.total_weight_stock_char == 0 and sales.total_weight_stock_srg != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="VV + Surg"
            if  sales.total_weight_stock_srg == sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0:
                sales.produitalivrer=" Charc"
            if sales.total_weight_stock_char != 0 and sales.total_weight_stock_srg != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="Charc + Surg + VV"
    