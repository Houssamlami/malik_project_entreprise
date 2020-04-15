# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging
from itertools import groupby
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError

_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    
    @api.onchange('qty_in_kg','qty_per_camion','product_id','price_unit')
    @api.depends('qty_in_kg','qty_per_camion','product_id','price_unit')
    def _prix_du_kilogramme(self):
        for record in self:
            if record.qty_in_kg and record.qty_in_kg !=0.0 and record.qty_per_camion != 0.0:
                record.price_kg = record.price_subtotal/record.qty_in_kg
                
    
    @api.onchange('km','product_id','price_unit','price_subtotal')
    @api.depends('km','product_id','price_unit','price_subtotal')
    def _prix_du_kilometre(self):
        for record in self:
            if record.product_id and record.km and record.price_subtotal != 0.0:
                record.price_km = record.km/record.price_subtotal
            
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
        
    @api.onchange('account_analytic_id','qty_in_kg','qty_per_camion')
    @api.depends('account_analytic_id','qty_in_kg','qty_per_camion')
    def _compute_ratio_camion(self):
        for record in self:
            if record.account_analytic_id and record.qty_in_kg and record.qty_per_camion:
                record.product_qty = record.qty_in_kg/record.qty_per_camion
        
    qty_in_kg = fields.Float(string="QTY en KG")
    qty_per_camion = fields.Float(string="QTY par camion")
    price_kg = fields.Float(string="Prix KG", compute='_prix_du_kilogramme', store=True)
    price_km = fields.Float(string="Prix KM", compute='_prix_du_kilometre', store=True)
    image_small = fields.Binary('Image', related='product_id.image_small')
    km = fields.Integer(string="KM", compute='_get_km_purchase_line')
    location_dest_id = fields.Many2one(comodel_name='stock.location', string='Destination')
    logistic = fields.Boolean(related='order_id.logistic', default=True, readonly=True)
    
    @api.onchange('order_id.logistic','order_id')
    @api.depends('order_id.logistic','order_id')
    def logistic_field(self):
        for record in self:
            record.logistic = record.order_id.logistic
