# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
import datetime
import time
from datetime import *


# Record the net weight of the order line
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'  
    
    
    @api.model
    def create(self, vals):
        if vals.get('secondary_uom_qty'):
            value = vals.get('secondary_uom_qty')
            vals['qty_initiale'] = value 
        result = super(SaleOrderLine,self).create(vals) 
        return result
    
    #Get Qty available in stock/ Qty demanded
    @api.multi
    @api.depends('product_id')
    def _compute_qty_disponible_en_stock(self):
        for line in self:
            qty_disponible_en_stock = 0
            if line.product_id:
                qty_disponible_en_stock = line.product_id.qty_available
            line.qty_disponible_en_stock = qty_disponible_en_stock

    @api.one
    def _set_qty_disponible_en_stock(self):
        pass
            

    @api.multi
    @api.depends('product_id')
    def _compute_qty_initial(self):
        for line in self:
            qty_initial_cmd = 0
            if line.product_id:
                qty_initial_cmd = line.product_uom_qty
            line.qty_initial_cmd = qty_initial_cmd

    @api.one
    def _set_qty_initial(self):
        pass
    

    weight = fields.Float(string='Weight(kg)', compute='_compute_weight',
                          inverse='_set_weight', store=True)
    volume = fields.Float(string='colis(unite)', compute='_compute_volume',
                          inverse='_set_volume', store=True)
    volume_tot = fields.Float(string='Prix Total', compute='_compute_volume_tot',
                          inverse='_set_volume_tot', store=True)
    qty_disponible_en_stock = fields.Float(string='qt', compute='_compute_qty_disponible_en_stock',
                          inverse='_set_qty_disponible_en_stock', store=True)                     
    qty_initial_cmd = fields.Float(string='qt initial', compute='_compute_qty_initial',
                          inverse='_set_qty_initial', store=True)
    
    test_on_change = fields.Float('Qte en tock reel')
    test_on_change_ver = fields.Float('Qte restante virtuell')
    test_on_change_version2= fields.Float('Qte a livre apre today')
    order_requested_date = fields.Datetime(related='order_id.requested_date', store=True, string=u'Date Demandée')
    qty_initiale = fields.Float(string='Qty initiale')
    product_service_commercial = fields.Boolean(string="CMD TTM")
    second_test = fields.Boolean(string="Second test")


    @api.onchange('price_unit')
    def onchange_price_unit_min(self):

        if (self.price_unit and self.price_unit < self.product_id.prix_min_vente):
            return {'warning': {
                'title': _('Prix de vente MIN!'),
                'message': _("Prix unitaire est inférieur au prix de vente minimum")
                }
            }
            
    @api.onchange('product_id')
    def on_change_state2(self):
        today = str(datetime.now().date())
        test_on_change_version2 = 0
        for record in self:
            if record.product_id:
                record.test_on_change = record.product_id.qty_available
                vouchers = self.env['sale.order'].search([('requested_date', '>', today)])
                productbl = self.env['sale.order.line'].search([
                ('product_id', '=', self.product_id.id),('order_id', 'in', vouchers.ids)])
                for rec in productbl:
                    test_on_change_version2 += rec.product_uom_qty
                    record.test_on_change_version2 = test_on_change_version2
                record.test_on_change_ver = record.test_on_change-record.test_on_change_version2
    # @api.onchange('product_id')
    # def on_change_state(self):
        # today = datetime.today()
        # Bolocagettm = 0
        # for record in self:
            # if record.product_id:
                # productbl = self.env['sale.order'].search([
                # ('requested_date', '>', '2019-01-01')])
                # Bolocagettm = productbl.id
                # self.env.cr.execute("""SELECT sum(product_uom_qty) as sum FROM sale_order_line where product_id = %(product_id)s  """, {'product_id':self.product_id.id})
                # record.test_on_change_ver = record.env.cr.fetchone()
                # record.test_on_change = record.product_id.qty_available
    
    @api.onchange('secondary_uom_qty')
    @api.depends('product_id', 'secondary_uom_qty')
    def _compute_weight(self):
        for line in self:
            weight = 0
            if line.product_id and line.product_id.weight:
                weight += (line.product_id.weight * line.secondary_uom_qty / line.product_uom.factor)
            line.weight = weight

    @api.one
    def _set_weight(self):
        pass

    @api.multi
    @api.depends('product_id', 'product_uom_qty',)
    def _compute_volume(self):
        for line in self:
            volume = 0
            if line.product_id and line.product_id.volume:
                volume += (line.product_id.volume * line.product_uom_qty / line.product_uom.factor)
            line.volume = volume

    @api.one
    def _set_volume(self):
        pass
		
    @api.multi
    @api.depends('volume', 'price_unit',)
    def _compute_volume_tot(self):
        for line in self:
            volume_tot = 0
            if line.product_id and line.price_unit:
                volume_tot = line.volume * line.price_unit
            line.volume_tot = volume_tot

    @api.one
    def _set_volume_tot(self):
        pass
    
    @api.multi
    def get_default_fact_qty(self):
        for line in self:
            qty_delivered = 0
            if line.product_id:
                pickings = self.env['stock.picking'].search([('origin', '=', line.order_id.name),('state','=','done'),('picking_type_code','=','outgoing')])
                sml = self.env['stock.move.line'].search([('picking_id', 'in', pickings.ids),('state','=','done')])
                if len(sml) != 0:
                    for lines in sml:
                        if line.product_id == lines.product_id:
                            qty_delivered += lines.qty_done
                    line.qty_delivered = qty_delivered
                else:
                    line.qty_delivered = 0
                    
            
    @api.multi
    def get_default_fact_qtys(self):
        for line in self:
            qty_invoiced = 0
            if line.product_id:
                invoices = self.env['account.invoice'].search([('origin', '=', line.order_id.name),('state','in',['paid','open'])])
                ail = self.env['account.invoice.line'].search([('invoice_id', 'in', invoice.ids)])
                if len(ail) != 0:
                    for lines in ail:
                        if line.product_id == lines.product_id:
                            qty_invoiced += lines.quantity
                    line.qty_invoiced = qty_invoiced
                else:
                    line.qty_invoiced = 0