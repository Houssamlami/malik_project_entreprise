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