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
    
    @api.multi
    @api.depends('picking_id.origin','quantity_done')
    def get_secondary_qty(self):
        for record in self:
            so = self.env['sale.order'].search([('name', '=', record.picking_id.origin)])
            for line in so.order_line:
                picking = record.picking_id
                if picking.picking_type_id.code == 'outgoing':
                    if record.product_id.name == line.product_id.name:
                        record.secondary_uom_qty = int(line.secondary_uom_qty)
                    #else:
                        #   record.secondary_uom_qty = 0.0
            if record.quantity_done != 0:
                if float_compare(record.product_uom_qty, record.quantity_done, precision_rounding=record.product_uom.rounding) >= 0:
                    unite = record.product_id
                    unit = unite.sale_secondary_uom_id
                    if unit.factor != 0:
                        record.secondary_uom_qty = int((record.quantity_done/unit.factor))

   
    @api.multi
    def write(self, vals):
        res = super(StockMove,self).write(vals)
        if (any(not record.lot_name or not record.date_reference for record in self.move_line_ids) and self.picking_id.picking_type_id.code == 'incoming'):
            return {'warning': {
                'title': _('Lot ou DLC!'),
                'message': _("Merci de mentionner le lot et DLC")
                }
            }
        return res
        
'''                    
    @api.multi
    def fill_lot_name_dlc(self):
        for move in self:
            if any(((not line.lot_name or not line.date_reference) and line.picking_id.picking_type_id.code == 'incoming') for line in move.move_line_ids):
                a = any(((not line.lot_name or not line.date_reference) and line.picking_id.picking_type_id.code == 'incoming') for line in move.move_line_ids)
                print(a)
                return {'warning': {
                'title': _('Lot ou DLC!'),
                'message': _("Merci de mentioner le lot et DLC")
                }
            }
          '''              
class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    date_dlc = fields.Datetime(related='lot_id.date_refer',
        string='DLC', store=True, readonly=True)
            