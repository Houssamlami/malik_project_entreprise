# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

   
    total_qty_ordred1 = fields.Float(string='Total qtyor', compute='_compute_colis_total_ordred')
    total_qty_delivred = fields.Float(string='Total delievred', compute='_compute_colis_total_delivred')
    total_qty_invoiced = fields.Float(string='Total invoiced', compute='_compute_colis_total_invoiced')
    etat_fac1 = fields.Char(string='Etat facture', compute='_compute_colis_total_etat')
    etat_fac1_copy = fields.Char(string='Etat facture copy', compute='_compute_colis_total_etat_copy',store=True)	
	

	
    def _compute_colis_total_ordred(self):
        for sale in self:
            total_qty_ordred1 = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_ordred1 += line.product_uom_qty or 0.0
            sale.total_qty_ordred1 = total_qty_ordred1

    def _compute_colis_total_delivred(self):
        for sale in self:
            total_qty_delivred = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_delivred += line.qty_delivered or 0.0
            sale.total_qty_delivred = total_qty_delivred

    def _compute_colis_total_invoiced(self):
        for sale in self:
            total_qty_invoiced = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_invoiced += line.qty_invoiced or 0.0
            sale.total_qty_invoiced = total_qty_invoiced

    def _compute_colis_total_etat(self):
        for sale in self:
            if sale.total_qty_invoiced == 0:
                sale.etat_fac1 = "A facturer"
            if sale.total_qty_invoiced > 0 :
                sale.etat_fac1 = "facturé"
				
    @api.depends('order_line.qty_invoiced','state')				
    def _compute_colis_total_etat_copy(self):
        for sale in self:
            if sale.total_qty_invoiced == 0:
                sale.etat_fac1_copy = "A facturer"
            if sale.total_qty_invoiced > 0 :
                sale.etat_fac1_copy = "Facturée"
            if sale.state == "cancel":
                sale.etat_fac1_copy = "Annulée"