# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang

from odoo.addons import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = "stock.picking"

    total_weight_stock_sec_auto = fields.Float(string='Total sec', compute='_compute_weight_total_stock_sec')
    total_weight_stock_frais_auto = fields.Float(string='Total frais)', compute='_compute_weight_total_stock_frais')
    total_weight_stock_surg_auto = fields.Float(string='Total surg)', compute='_compute_weight_total_stock_surg')
    total_weight_stock_volailles_auto = fields.Float(string='Total volailles)', compute='_compute_weight_total_stock_volailles')

    def _compute_weight_total_stock_sec(self):
        for stock in self:
            weight_stock_sec = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name =="Sec":
                    weight_stock_sec += line.product_uom_qty  or 0.0
            stock.total_weight_stock_sec_auto = weight_stock_sec

    def _compute_weight_total_stock_frais(self):
        for stock in self:
            weight_stock_frais = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name == "Frais":
                    weight_stock_frais += line.product_uom_qty  or 0.0
            stock.total_weight_stock_frais_auto = weight_stock_frais

    def _compute_weight_total_stock_surg(self):
        for stock in self:
            weight_stock_surg = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name == "Surgelé":
                    weight_stock_surg += line.product_uom_qty  or 0.0
            stock.total_weight_stock_surg_auto = weight_stock_surg

    def _compute_weight_total_stock_volailles(self):
        for stock in self:
            weight_stock_volailles = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name == "Volailles":
                    weight_stock_volailles += line.product_uom_qty  or 0.0
            stock.total_weight_stock_volailles_auto = weight_stock_volailles