# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from setuptools import depends
from passlib.tests.utils import limit
from reportlab.lib.pdfencrypt import computeO
from odoo.tools import float_compare, float_round, float_repr
from odoo.addons import decimal_precision as dp
import string


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    
    @api.depends('kilometre','prix_transp','qty_totals')
    @api.onchange('prix_transp','kilometre','qty_totals')
    def _on_change_kilometre(self):
         for record in self:
             record._get_prix_par_km()
             record._get_prix_par_kg()
             
    @api.depends('prix_transp')
    @api.onchange('prix_transp')
    def _on_change_prix_transp(self):
         for record in self:
             record._get_prix_par_km()
             record._get_prix_par_kg()
             
             
    @api.depends('order_line.price_subtotal')
    def _get_prix_transport(self):
        for record in self:
            obj = self.env['purchase.order.line'].search([('order_id', '=', record.id)], limit=1)
            if len(obj) != 0:            
                record.prix_transp = obj.price_subtotal
                
                
    @api.depends('kilometre','prix_transp')
    def _get_prix_par_km(self):
        for record in self:
            precision = self.env['decimal.precision'].precision_get('Product Price')
            if record.kilometre != 0:
                record.prix_par_km = float_round(record.prix_transp/record.kilometre, precision_digits=precision)
            
    @api.depends('qty_totals','prix_transp')
    def _get_prix_par_kg(self):
        for record in self:
            precision = self.env['decimal.precision'].precision_get('Product Price')
            if record.qty_totals != 0:
                record.prix_par_kg = float_round(record.prix_transp/record.qty_totals, precision_digits=precision)
                
    @api.depends('order_line.product_id')
    def _get_km(self):
        for record in self:
            obj = self.env['purchase.order.line'].search([('order_id', '=', record.id)], limit=1)
            if len(obj) != 0:            
                record.kilometre = obj.km
            
                
    qty_totals = fields.Float(string=u"Quantité Transportée(KG)", compute='_get_totals_qty', store=True , readonly=True)
    logistic = fields.Boolean(string="Logistic")
    kilometre = fields.Float(string=u"Kilométrage(KM)", compute='_get_km', store=True)
    prix_transp = fields.Float(string=u"Coût Transport", compute='_get_prix_transport', store=True)
    prix_par_km = fields.Float(string=u"Prix par KM", compute='_get_prix_par_km', store=True ,readonly=True)
    prix_par_kg = fields.Float(string=u"Prix par KG", compute='_get_prix_par_kg', store=True, readonly=True)
    data_file_cmr = fields.Binary(string='Fichier CMR')
    purchase_order_id = fields.Many2one(comodel_name='purchase.order', string=u'BC Achat', domain=[('partner_id.name', 'in', ('imex','bona'))])
    
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            if order.logistic and not order.data_file_cmr:
                raise UserError(_("Merci de joindre un fichier CMR."))
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
    
        
    @api.multi
    @api.depends('purchase_order_id')
    def _get_totals_qty(self):
        for record in self:
            cmpt = 0
            if record.purchase_order_id:
                obj = self.env['purchase.order'].search([('id', '=', record.purchase_order_id.id)])
                for lines in obj.order_line:
                    if lines.product_id:
                        cmpt += lines.product_qty
            record.qty_totals = cmpt
        
        
    @api.onchange('order_line.price_unit')
    def _on_change_orderline(self):
         for record in self:
             record._get_totals_qty()
    
    @api.onchange('purchase_order_id')
    def _on_change_purchaseorderid(self):
        for record in self:
            record._get_totals_qty()
        


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    
    @api.depends('product_id')
    def _get_km_purchase_line(self):
        if not self.product_id:
            return
         
        seller = self.product_id._select_seller(
            partner_id=self.partner_id,
            quantity=self.product_qty,
            date=self.order_id.date_order and self.order_id.date_order[:10],
            uom_id=self.product_uom)
        
        self.km = seller.nbr_km
        
        
    image_small = fields.Binary('Image', related='product_id.image_small')
    km = fields.Integer(string="KM", compute='_get_km_purchase_line')
    
    
        
    