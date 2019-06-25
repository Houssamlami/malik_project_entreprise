# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    
    

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
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
                
                
                