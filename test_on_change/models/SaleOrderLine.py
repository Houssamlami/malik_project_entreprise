# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
import datetime
import time
from datetime import *


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    test_on_change = fields.Float('qte en tock reel')
    test_on_change_ver = fields.Float('qte restante virtuell')
    test_on_change_version2= fields.Float('qte a livre apre today')


    @api.onchange('product_id')
    def on_change_state2(self):
        today = str(datetime.now().date())
        test_on_change_version2 = 0
        for record in self:
            if record.product_id:
                record.test_on_change = record.product_id.qty_available
                vouchers = self.env['sale.order'].search([('requested_date', '>', today)])
                productbl = self.env['sale.order.line'].search([
                ('product_id', '=', self.product_id.id),('order_id', 'in', vouchers.ids)])
                for rec in productbl:
                    test_on_change_version2 += rec.product_uom_qty
                    record.test_on_change_version2 = test_on_change_version2
                record.test_on_change_ver = record.test_on_change-record.test_on_change_version2
    # @api.onchange('product_id')
    # def on_change_state(self):
        # today = datetime.today()
        # Bolocagettm = 0
        # for record in self:
            # if record.product_id:
                # productbl = self.env['sale.order'].search([
                # ('requested_date', '>', '2019-01-01')])
                # Bolocagettm = productbl.id
                # self.env.cr.execute("""SELECT sum(product_uom_qty) as sum FROM sale_order_line where product_id = %(product_id)s  """, {'product_id':self.product_id.id})
                # record.test_on_change_ver = record.env.cr.fetchone()
                # record.test_on_change = record.product_id.qty_available