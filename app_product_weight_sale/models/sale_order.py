# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_weight = fields.Float(string='Total Weight(kg)', compute='_compute_weight_total')
    total_colis = fields.Float(string='Total colis', compute='_compute_colis_total')
    total_volume_ht = fields.Float(string='Montant Total TTC', compute='_compute_volumeht_total')
    total_ht = fields.Float(string='Montant Total HT', compute='_compute_ht_total')

    def _compute_weight_total(self):
        for sale in self:
            weight_tot = 0
            for line in sale.order_line:
                if line.product_id:
                    weight_tot += line.weight or 0.0
            sale.total_weight = weight_tot
			
    def _compute_colis_total(self):
        for sale in self:
            total_colis = 0
            for line in sale.order_line:
                if line.product_id:
                    total_colis += line.product_uom_qty or 0.0
            sale.total_colis = total_colis
			
    def _compute_volumeht_total(self):
        for sale in self:
            total_volum_ht = 0
            for line in sale.order_line:
                if line.product_id:
                    total_volum_ht += (line.volume_tot * (line.tax_id.amount/100))+line.volume_tot or 0.0
            sale.total_volume_ht = total_volum_ht

    def _compute_ht_total(self):
        for sale in self:
            total_ht = 0
            for line in sale.order_line:
                if line.product_id:
                    total_ht += line.volume_tot or 0.0
            sale.total_ht = total_ht