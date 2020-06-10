# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    nbr_colis = fields.Char(string="Nbr of colis")
    custumer_note = fields.Text(string="Note")
    signature = fields.Binary(string='Signature')
    livreur = fields.Many2one('res.partner',string='Livreur', readonly=True)
    state = fields.Selection(selection_add=[
        ('emarge', 'Émargé'),
        ('retour', 'Retour Entrepôt'),
    ])

    reception_type = fields.Selection(
        [
            ('complete', 'Complete'),
            ('partielle', 'Partielle'),
            ('refus', 'Refus'),
        ],
        required=True,
        string='Type de réception'
    )
    motif = fields.Many2one('alb.motif', string='Raison')
    action = fields.Selection(
        [
            ('rw,', 'Retour à l’entrepôt'),
            ('rwd', 'Retour à l’entrepôt et re-livraison'),
        ],
        string='Action'
    )

    def customer_reception(self):
        action = self.env.ref('alb_delivery_sign.action_custumer_reception').read()[0]
        action['context'] = {'default_picking_id': self.id}
        action['views'] = [(self.env.ref('alb_delivery_sign.custumer_reception_wizard').id, 'form')]
        return action
