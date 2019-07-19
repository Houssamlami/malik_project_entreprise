# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang

from odoo.addons import decimal_precision as dp


class StockPicking(models.Model):
    _inherit = "stock.picking"

    total_weight_stock_sec = fields.Float(string='Total sec', compute='_compute_weight_total_stock_sec')
    total_weight_stock_frais = fields.Float(string='Total frais)', compute='_compute_weight_total_stock_frais')
    total_weight_stock_surg = fields.Float(string='Total surg)', compute='_compute_weight_total_stock_surg')
    total_weight_stock_volailles = fields.Float(string='Total volailles)', compute='_compute_weight_total_stock_volailles')

    def _compute_weight_total_stock_sec(self):
        for stock in self:
            weight_stock_sec = 0
            for line in stock.move_lines:
                if line.product_id.categ_id.parent_id.name in ("Sauces","Chips"):
                    weight_stock_sec += line.product_uom_qty  or 0.0
            stock.total_weight_stock_sec = weight_stock_sec
			
    def _compute_weight_total_stock_frais(self):
        for stock in self:
            weight_stock_frais = 0
            for line in stock.move_lines:
                if line.product_id.categ_id.parent_id.name in ("Saucissons","Chapelet","Mortadelle","Blocs","Panes","Tranches"):
                    weight_stock_frais += line.product_uom_qty  or 0.0
            stock.total_weight_stock_frais = weight_stock_frais
			
    def _compute_weight_total_stock_surg(self):
        for stock in self:
            weight_stock_surg = 0
            for line in stock.move_lines:
                if line.product_id.categ_id.parent_id.name in ("Surgeles","IQF"):
                    weight_stock_surg += line.product_uom_qty  or 0.0
            stock.total_weight_stock_surg = weight_stock_surg
			
    def _compute_weight_total_stock_volailles(self):
        for stock in self:
            weight_stock_volailles = 0
            for line in stock.move_lines:
                if line.product_id.categ_id.parent_id.name in ("Volaille","Volailles Espagne","La Volailles BON","Volailles IMEX"):
                    weight_stock_volailles += line.product_uom_qty  or 0.0
            stock.total_weight_stock_volailles = weight_stock_volailles
			