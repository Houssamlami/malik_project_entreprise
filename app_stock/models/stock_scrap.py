# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils


class ScrapReason(models.Model):
    _name = "reason.scrap"
    _description = "Scrap reason"
    
    name = fields.Char(string="Raison de rebut")


class StockScrap(models.Model):
    _inherit = "stock.scrap"
    _description = "Stock scrap"
    
    scrap_local = state = fields.Selection([('internal', 'Interne'),('external', 'Externe')], string='Lieu de rebut', default="internal")
    scrap_reason_id = fields.Many2one('reason.scrap', string="Raison de rebut")
    comment = fields.Text(string="Commentaire")