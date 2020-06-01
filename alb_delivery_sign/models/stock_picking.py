# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    nbr_colis = fields.Char(string="Nbr of colis")
    custumer_note = fields.Text(string="Note")
    signature = fields.Binary(string='Signature')
    state = fields.Selection(selection_add=[
        ('emarge', 'Émargé')
    ])

    def customer_reception(self):
        action = self.env.ref('alb_delivery_sign.action_custumer_reception').read()[0]
        action['context'] = {'default_picking_id': self.id}
        action['views'] = [(self.env.ref('alb_delivery_sign.custumer_reception_wizard').id, 'form')]
        return action
