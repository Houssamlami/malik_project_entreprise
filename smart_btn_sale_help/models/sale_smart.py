# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from dateutil import relativedelta
from datetime import datetime, timedelta
import time

# Record the net weight of the order line
class sale_order(models.Model):
    _inherit = 'sale.order'


# Record the net weight of the order line
class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    @api.depends('product_id')
    def _compute_qty_disponible_en_stock(self):
        for line in self:
            qty_disponible_en_stock = 0
            if line.product_id:
                qty_disponible_en_stock = line.product_id.qty_available
            line.qty_disponible_en_stock = qty_disponible_en_stock

    @api.one
    def _set_qty_disponible_en_stock(self):
        pass
		
		

		
		
    qty_disponible_en_stock = fields.Float(string='qt', compute='_compute_qty_disponible_en_stock',
                          inverse='_set_qty_disponible_en_stock', store=True)
						  
    qty_initial_cmd = fields.Float(string='qt initial', compute='_compute_qty_initial',
                          inverse='_set_qty_initial', store=True)



    @api.multi
    @api.depends('product_id')
    def _compute_qty_initial(self):
        for line in self:
            qty_initial_cmd = 0
            if line.product_id:
                qty_initial_cmd = line.product_uom_qty
            line.qty_initial_cmd = qty_initial_cmd

    @api.one
    def _set_qty_initial(self):
        pass


						  
class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def _sales_count2(self):
        r = {}
        if not self.user_has_groups('sales_team.group_sale_salesman'):
            return r
        domain = [
            ('product_id', 'in', self.ids),
        ]
        for group in self.env['sale.report'].read_group(domain, ['product_id', 'product_uom_qty'], ['product_id']):
            r[group['product_id'][0]] = group['product_uom_qty']
        for product in self:
            product.sales_count2 = r.get(product.id, 0)
        return r

    sales_count2 = fields.Integer(compute='_sales_count2', string='# Salesss')

	


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
