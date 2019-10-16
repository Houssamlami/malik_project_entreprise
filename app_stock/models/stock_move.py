# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import split_every
from psycopg2 import OperationalError

from odoo import api, fields, models, registry, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round

from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)




class StockMove(models.Model):
    _inherit = 'stock.move'
    
    secondary_uom_qty = fields.Float(compute='get_secondary_qty', string="Box")
    secondary_uom_qty_regul = fields.Float(string="Colis", readonly=False, track_visibility='onchange')
    unite_is_kg = fields.Boolean(compute='get_unit_move')
    
    def get_unit_move(self):
        for record in self:
            if record.product_id.uom_id.name =='kg':
                record.unite_is_kg = True
            else:
                record.unite_is_kg = False
                
    def _update_secondary_uom_qty_regul(self, values):
        for line in self:
            pickings = line.picking_id.filtered(lambda p: p.state not in ('cancel'))
            for picking in pickings:
                picking.message_post("Colis du %s a été changé de %d à %d" %
                                      (line.product_id.display_name, line.secondary_uom_qty_regul, values['secondary_uom_qty_regul']))

    
    @api.multi
    @api.depends('picking_id.origin','quantity_done')
    def get_secondary_qty(self):
        for record in self:
            so = self.env['sale.order'].search([('name', '=', record.picking_id.origin)])
            if record.picking_type_id.code == 'incoming':
                returns = self.env['stock.picking'].search([('group_id', '=', record.picking_id.group_id.id),('state','=','done'),('picking_type_id.code','=','outgoing')])
                if returns and record.picking_type_id.code == 'incoming':
                    for lines in returns.move_lines.filtered(lambda s: s.product_id.id == record.product_id.id):
                        record.secondary_uom_qty = lines.secondary_uom_qty
            for line in so.order_line:
                picking = record.picking_id
                if picking.picking_type_id.code == 'outgoing':
                    if record.product_id.name == line.product_id.name:
                        record.secondary_uom_qty = int(line.secondary_uom_qty)
            
                    #else:
                        #   record.secondary_uom_qty = 0.0
            if record.quantity_done != 0:
                if abs(float_compare(record.sale_line_id.product_uom_qty, record.quantity_done, precision_rounding=record.product_uom.rounding))>= 0:
                    unite = record.product_id
                    unit = unite.sale_secondary_uom_id
                    if unit.factor != 0 and record.sale_line_id.product_uom_qty-record.quantity_done <= ((-1)* unit.factor) and unite.uom_id.name =='kg' :
                        record.secondary_uom_qty = int(record.secondary_uom_qty)+ int((record.quantity_done-record.sale_line_id.product_uom_qty)/unit.factor)
                    if unit.factor != 0 and record.sale_line_id.product_uom_qty-record.quantity_done >= (unit.factor) and unite.uom_id.name =='kg' :
                        record.secondary_uom_qty = int(record.sale_line_id.secondary_uom_qty) - int((record.sale_line_id.product_uom_qty-record.quantity_done)/unit.factor)
                    if unite.uom_id.name !='kg' and abs(record.sale_line_id.secondary_uom_qty-record.quantity_done) > 0:
                        record.secondary_uom_qty = record.quantity_done
                    if record.quantity_done != 0 and record.secondary_uom_qty_regul != 0.0:
                        record.secondary_uom_qty = record.secondary_uom_qty_regul
            if record.quantity_done != 0 and record.picking_code == 'incoming':
                unite = record.product_id
                unit = unite.sale_secondary_uom_id
                if unit.factor != 0 and unite.uom_id.name =='kg' :
                    record.secondary_uom_qty = int((record.quantity_done)/unit.factor)
                if unite.uom_id.name !='kg' and abs(record.sale_line_id.secondary_uom_qty-record.quantity_done) >= 0:
                    record.secondary_uom_qty = record.quantity_done
                        
    def action_modify_colis(self):
       
        self.ensure_one()
        if self.picking_id.picking_type_id.code == 'outgoing':
            view = self.env.ref('app_stock.view_stock_move_change_colis')
        return {
            'name': _('Change colis'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            
            
        }
        
    
        
    @api.multi
    def write(self, values):
        if 'secondary_uom_qty_regul' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            self.filtered(
                lambda r: r.state not in 'cancel' and float_compare(r.secondary_uom_qty_regul, values['secondary_uom_qty_regul'], precision_digits=precision) != 0)._update_secondary_uom_qty_regul(values)
        result = super(StockMove, self).write(values)
        return result
        
    @api.multi
    def action_accept_colis(self):
        
        for wiz in self:
            picking = self.env['stock.move'].browse(self.env.context['active_id'])
            wiz.write({'secondary_uom_qty': wiz.secondary_uom_qty_regul})
            wiz.get_secondary_qty()
            
  
              
class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    date_dlc = fields.Datetime(related='lot_id.date_refer',
        string='DLC', store=True, readonly=True)
            