# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.addons import decimal_precision as dp

from datetime import datetime, timedelta
from datetime import datetime
import datetime


class StockPicking(models.Model):
    _inherit = "stock.picking"

    total_weight_stock_sec_auto = fields.Float(string='Total sec', compute='_compute_weight_total_stock_sec')
    total_weight_stock_frais_auto = fields.Float(string='Total frais)', compute='_compute_weight_total_stock_frais')
    total_weight_stock_surg_auto = fields.Float(string='Total surg)', compute='_compute_weight_total_stock_surg')
    total_weight_stock_volailles_auto = fields.Float(string='Total volailles)', compute='_compute_weight_total_stock_volailles')
    total_colis_delivered = fields.Float(string='Total Colis', compute='_compute_colis_poids_total_bl')
    total_weight_delivered = fields.Float(string='Poids Total', compute='_compute_colis_poids_total_bl')
    
    def _compute_colis_poids_total_bl(self):
        for picking in self:
            total_colis = 0
            total_poids = 0
            for line in picking.move_lines:
                if line.product_id:
                    total_poids += (line.quantity_done or 0.0)*line.product_id.weight
                    total_colis += (line.secondary_uom_qty or 0.0)
            picking.total_weight_delivered = total_poids
            picking.total_colis_delivered = total_colis

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
            
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    
        
    date_refer = fields.Datetime(string="Date référence", default=fields.Date.today())
    
    
    def _get_dates(self, product_id=None):
        """Returns dates based on number of days configured in current lot's product."""
        mapped_fields = {
            'life_date': 'life_time',
            'use_date': 'use_time',
            'removal_date': 'removal_time',
            'alert_date': 'alert_time'
        }
        
        str_date = str(self.date_refer)
        date_r = datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
        res = dict.fromkeys(mapped_fields, False)
        product = self.env['product.product'].browse(product_id) or self.product_id
        if product:
            i=0
            for field in mapped_fields:
                duration = getattr(product, mapped_fields[field])
                if duration and field != 'life_date':
                    date = date_r + datetime.timedelta(days=duration)
                    res[field] = fields.Datetime.to_string(date)              
                if field == 'life_date':
                    date = date_r + datetime.timedelta(days=0)
                    res[field] = fields.Datetime.to_string(date)
                i = i+1
        return res
    
    @api.model
    def create(self, vals):
        lot = super(StockProductionLot, self).create(vals)
        dates = lot._get_dates(vals.get('product_id') or self.env.context.get('default_product_id'))
        for d in dates:
            if not vals.get(d):
                vals[d] = dates[d]
        return lot
    
    @api.onchange('date_refer')
    def _onchange_date_refer(self):
        dates_dict = self._get_dates()
        for field, value in dates_dict.items():
            setattr(self, field, value)