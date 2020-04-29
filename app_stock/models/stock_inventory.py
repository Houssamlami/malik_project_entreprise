# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils





class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"
    _description = "Inventory Line"
    
    
    date_refer = fields.Datetime(string=u"DLC", related='prod_lot_id.date_refer')
    qty_colis_stock = fields.Float(related='product_id.secondary_unit_qty_available', string=u"Qty théorique Colis")
    qty_colis_stock_real = fields.Float(string=u"Qty Réelle Colis")
    difference_qty = fields.Float(string=u"Ecart")
    
    
    @api.onchange('product_qty')
    @api.depends('product_qty')
    def onchange_quantity_product_real(self):
        if self.product_id:
            self.difference_qty = self.theoretical_qty - self.product_qty
    
    
    @api.onchange('product_id', 'location_id', 'product_uom_id', 'prod_lot_id', 'package_id')
    def onchange_quantity_context_colis(self):
        if self.product_id and self.location_id and self.product_id.uom_id.category_id == self.product_uom_id.category_id:  # TDE FIXME: last part added because crash
            self.qty_colis_stock_real = self.qty_colis_stock
            
            
class StockInventory(models.Model):
    _inherit = "stock.inventory"
    _description = "Inventory"  
     
    def action_done(self):
        negative = next((line for line in self.mapped('line_ids') if line.product_qty < 0 and line.product_qty != line.theoretical_qty), False)
        if negative:
            raise UserError(_('You cannot set a negative product quantity in an inventory line:\n\t%s - qty: %s') % (negative.product_id.name, negative.product_qty))
        self.action_check()
        self.write({'state': 'done'})
        self.post_inventory()
        for line in self.line_ids:
            line.product_id.secondary_unit_qty_available = line.qty_colis_stock_real
        return True