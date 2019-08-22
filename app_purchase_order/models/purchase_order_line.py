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
    
    
    @api.onchange('qty_in_kg')
    @api.depends('qty_in_kg')
    def _prix_du_kilogramme(self):
        for record in self:
            if record.qty_in_kg and record.qty_in_kg !=0.0:
                record.price_kg = record.price_subtotal/record.qty_in_kg
            
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
        
    qty_in_kg = fields.Float(string="GTY en KG")
    price_kg = fields.Float(string="Prix KG", compute='_prix_du_kilogramme', store=True)
    image_small = fields.Binary('Image', related='product_id.image_small')
    km = fields.Integer(string="KM", compute='_get_km_purchase_line')
    location_dest_id = fields.Many2one(comodel_name='stock.location', string='Destination')
    logistic = fields.Boolean(related='order_id.logistic', store=True)
    
    @api.onchange('order_id.logistic','order_id')
    @api.depends('order_id.logistic','order_id')
    def logistic_field(self):
        for record in self:
            record.logistic = record.order_id.logistic
