# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, _
import datetime
import time
from datetime import *


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    test_on_change = fields.Float('qte en tock reel')
    test_on_change_ver = fields.Float('qte restante virtuelle')
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
                # record.test_on_change_ver = record.test_on_change-record.test_on_change_version2
                if record.product_id.uom_id.id==3:
                    record.test_on_change_ver = round(((record.test_on_change-record.test_on_change_version2)/record.product_id.weight)) or 0.00
                else:
                    record.test_on_change_ver = round((record.test_on_change-record.test_on_change_version2))
				
				
				
class ProductTemplate(models.Model):

    _inherit = 'product.template'

    test_on_product = fields.Float('qte en tock reel', compute='on_product_state2')
    test_on_product_ver = fields.Float('qte restante virtuell', compute='on_product_state2')
    test_on_product_ver_colis_for_kg = fields.Float('qte restante virtuell en colis ', compute='on_product_state2')
    test_on_product_version2= fields.Float('qte a livre apre today',compute='on_product_state2')
    test_on_product_version3= fields.Integer('qte a livre apre today3',compute='on_product_state2')
    test_on_product_vertuel_jours_suivant2= fields.Float('max qty disponible en stock le jour j',compute='on_product_vertuel_jours_suivant')
    total_commande_jour_suivant= fields.Float('qte a livre le jour j+1',compute='on_product_vertuel_jours_suivant')
    stock_virtuel_jour_suivant= fields.Float('qte en tock virtuel le jour j+1',compute='on_product_vertuel_jours_suivant')
#    @api.depends('id')
    def on_product_state2(self):
        today = str(datetime.now().date())
        test_on_product_version2 = 0
        test_on_product_version3 = 0
        for record in self:
            if record.id:
                record.test_on_product = record.qty_available
                record.test_on_product_version3 = self.env['product.product'].search([('product_tmpl_id', '=', record.id)],limit=1).id
                vouchers = self.env['sale.order'].search([('requested_date', '>', today)])
                productbl = self.env['sale.order.line'].search([
                ('product_id', '=', record.test_on_product_version3),('qty_delivered', '=', 0),('order_id', 'in', vouchers.ids)])
                for rec in productbl:
                    test_on_product_version2 += rec.product_uom_qty
                record.test_on_product_version2 = test_on_product_version2
                record.test_on_product_ver = record.test_on_product-record.test_on_product_version2
                if record.weight>0 and record.uom_id.id==3:
                        record.test_on_product_ver_colis_for_kg = round((record.test_on_product_ver/record.weight))
						
						
#cette fonction permet de calculer les qte a livrer j+1 (les commande saisie de la jour j) et la qte qui doit rester en stock le jour j 				
						
    def on_product_vertuel_jours_suivant(self):
        today = datetime.today()
        test_on_product_vertuel_jours_suivant2 = 0
        test_on_product_vertuel_jours_suivant3 = 0
        max_id= 0
        total_commande_jour_suivant= 0
        stock_virtuel_jour_suivant= 0
        for record in self:
            if record.id:
                record.test_on_product_vertuel_jours_suivant3 = self.env['product.product'].search([('product_tmpl_id', '=', record.id)]).id
                vouchers = self.env['sale.order'].search([('requested_date', '>', (today + timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')), ('requested_date', '<', (today + timedelta(days=1)).strftime('%Y-%m-%d 23:59:59'))])
                productbl = self.env['sale.order.line'].search([
                ('product_id', '=', record.test_on_product_vertuel_jours_suivant3),('qty_delivered', '=', 0),('order_id', 'in', vouchers.ids)])
                for rec in productbl:
                    max_id = max(rec).qty_disponible_en_stock
                    total_commande_jour_suivant += rec.product_uom_qty
                if record.weight>0 and record.uom_id.id==3:
                    record.test_on_product_vertuel_jours_suivant2 = round((max_id/record.weight))
                    record.total_commande_jour_suivant = round((total_commande_jour_suivant/record.weight))
                    record.stock_virtuel_jour_suivant = record.test_on_product_vertuel_jours_suivant2 - record.total_commande_jour_suivant
                else :
                    record.test_on_product_vertuel_jours_suivant2 = max_id
                    record.total_commande_jour_suivant = total_commande_jour_suivant
                    record.stock_virtuel_jour_suivant = record.test_on_product_vertuel_jours_suivant2 - record.total_commande_jour_suivant
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