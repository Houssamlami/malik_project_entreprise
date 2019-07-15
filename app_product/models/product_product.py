# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from dateutil import relativedelta
from datetime import datetime, timedelta
import time


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