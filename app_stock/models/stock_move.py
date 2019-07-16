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
                        record.secondary_uom_qty = line.secondary_uom_qty
                    #else:
                     #   record.secondary_uom_qty = 0.0
            if record.quantity_done != 0:
                if float_compare(record.product_uom_qty, record.quantity_done, precision_rounding=record.product_uom.rounding) >= 0:
                    unite = record.product_id
                    unit = unite.sale_secondary_uom_id
                    if unit.factor != 0:
                        record.secondary_uom_qty = (record.quantity_done/unit.factor)
            