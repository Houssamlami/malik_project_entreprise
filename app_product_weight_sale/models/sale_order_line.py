# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


# Record the net weight of the order line
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    weight = fields.Float(string='Weight(kg)', compute='_compute_weight',
                          inverse='_set_weight', store=True)
    volume = fields.Float(string='colis(unite)', compute='_compute_volume',
                          inverse='_set_volume', store=True)
    volume_tot = fields.Float(string='Prix Total', compute='_compute_volume_tot',
                          inverse='_set_volume_tot', store=True)

    @api.multi
    @api.depends('product_id', 'product_uom_qty')
    def _compute_weight(self):
        for line in self:
            weight = 0
            if line.product_id and line.product_id.weight:
                weight += (line.product_id.weight * line.product_uom_qty * line.product_id.volume / line.product_uom.factor)
            line.weight = weight

    @api.one
    def _set_weight(self):
        pass

    @api.multi
    @api.depends('product_id', 'product_uom_qty',)
    def _compute_volume(self):
        for line in self:
            volume = 0
            if line.product_id and line.product_id.volume:
                volume += (line.product_id.volume * line.product_uom_qty / line.product_uom.factor)
            line.volume = volume

    @api.one
    def _set_volume(self):
        pass
		
    @api.multi
    @api.depends('volume', 'price_unit',)
    def _compute_volume_tot(self):
        for line in self:
            volume_tot = 0
            if line.product_id and line.price_unit:
                volume_tot = line.volume * line.price_unit
            line.volume_tot = volume_tot

    @api.one
    def _set_volume_tot(self):
        pass