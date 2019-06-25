# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import datetime
import time
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP


class ProductTemplate(models.Model):
    _inherit = 'product.template'


    @api.multi
    @api.depends('product_variant_ids.sales_count2')
    def _sales_count2(self):
        for product in self:
            product.sales_count2 = sum([p.sales_count2 for p in product.with_context(active_test=False).product_variant_ids])

    @api.multi
    def action_view_saless(self):
        self.ensure_one()
        action = self.env.ref('smart_btn_sale_help.action_product_sale_list34')
        product_ids = self.with_context(active_test=False).product_variant_ids.ids

        return {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': "{'default_product_id': " + str(product_ids[0]) + "}",
            'res_model': action.res_model,
            'domain': [('product_id.product_tmpl_id', '=', self.id)],
        }

    sales_count2 = fields.Integer(compute='_sales_count2', string='# Salesss')
	
