# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging
from itertools import groupby
from odoo import models, api, fields, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.float_utils import float_is_zero, float_compare

_logger = logging.getLogger(__name__)

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    
    @api.multi
    def _create_or_update_picking(self):
        for line in self:
            if line.product_id.type in ('product', 'consu'):
                # Prevent decreasing below received quantity
                if float_compare(line.product_qty, line.qty_received, line.product_uom.rounding) < 0:
                    raise UserError('You cannot decrease the ordered quantity below the received quantity.\n'
                                    'Create a return first.')

                if float_compare(line.product_qty, line.qty_invoiced, line.product_uom.rounding) == -1:
                    # If the quantity is now below the invoiced quantity, create an activity on the vendor bill
                    # inviting the user to create a refund.
                    activity = self.env['mail.activity'].sudo().create({
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'note': _('The quantities on your purchase order indicate less than billed. You should ask for a refund. '),
                        'res_id': line.invoice_lines[0].invoice_id.id,
                        'res_model_id': self.env.ref('account.model_account_invoice').id,
                    })
                    activity._onchange_activity_type_id()

                # If the user increased quantity of existing line or created a new line
                pickings = line.order_id.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel') and x.location_dest_id.usage in ('internal', 'transit'))
                picking = pickings and pickings[0] or False
                if not picking:
                    res = line.order_id._prepare_picking(self.location_dest_id)
                    picking = self.env['stock.picking'].create(res)
                move_vals = line._prepare_stock_moves(picking)
                for move_val in move_vals:
                    self.env['stock.move']\
                        .create(move_val)\
                        ._action_confirm()\
                        ._action_assign()
                        
    @api.onchange('qty_in_kg','qty_per_camion','product_id','price_unit')
    @api.depends('qty_in_kg','qty_per_camion','product_id','price_unit')
    def _prix_du_kilogramme(self):
        for record in self:
            if record.qty_in_kg and record.qty_in_kg !=0.0 and record.qty_per_camion != 0.0:
                record.price_kg = record.price_subtotal/record.qty_in_kg
                
    
            
    @api.onchange('product_id')
    @api.depends('product_id')
    def _get_km_purchase_line(self):
        for record in self:
            
            if not record.product_id:
                return
         
            seller = record.product_id._select_seller(
                partner_id=record.partner_id,
                quantity=record.product_qty,
                date=record.order_id.date_order and record.order_id.date_order[:10],
                uom_id=record.product_uom)
        
            record.km = seller.nbr_km
        
    @api.onchange('product_id','price_unit','price_subtotal')
    @api.depends('product_id','price_unit','price_subtotal')
    def _prix_du_kilometre(self):
        for record in self:
            if record.product_id and record.km and record.price_subtotal != 0.0:
                record.price_km = record.price_unit/record.km
        
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
