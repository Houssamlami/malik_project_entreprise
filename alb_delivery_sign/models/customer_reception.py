# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CustomerReception(models.TransientModel):
    _name = 'customer.reception.wizard'

    picking_id = fields.Many2one('stock.picking', string="Operation")
    partner_id = fields.Many2one(string="Partner", related="picking_id.partner_id")
    pin = fields.Char(string="PIN")
    nbr_colis = fields.Char(string="Nbr of colis")
    custumer_note = fields.Text(string="Note")
    signature =  fields.Binary(string='Signature')

    def validate(self):
        for r in self:
            if r.pin == r.partner_id.pin:
                r.picking_id.nbr_colis = r.nbr_colis
                r.picking_id.custumer_note = r.custumer_note
                r.picking_id.signature = r.signature
                r.picking_id.state = 'emarge'
            else:
                raise ValidationError(_('The pin is incorrect'))