# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class CustomerReception(models.TransientModel):
    _name = 'customer.reception.wizard'

    picking_id = fields.Many2one('stock.picking', string="Operation")
    partner_id = fields.Many2one(string="Partner", related="picking_id.partner_id")
    pin = fields.Char(string="PIN Client")
    pin_livreur = fields.Char(string="PIN Livreur")
    nbr_colis = fields.Char(string="Nbr of colis")
    custumer_note = fields.Text(string="Note")
    signature = fields.Binary(string='Signature')
    reception_type = fields.Selection(
        [
            ('complete', 'Complete'),
            ('partielle', 'Partielle'),
            ('refus', 'Refus'),
        ],
        default='complete',
        string='Type de réception'
    )
    confirmite = fields.Selection(
        [
            ('conforme', 'Conforme'),
            ('nnconforme', 'Non Conforme'),
        ],
        
        string='Confirmité'
    )
    motif = fields.Many2one('alb.motif', string='Raison')
    action = fields.Selection(
        [
            ('rw', 'Retour à l’entrepôt'),
            ('rwd', 'Retour à l’entrepôt et re-livraison'),
            ('rwdr','Retour à l’entrepôt et remise en stock'),
        ],
        string='Action'
    )

    def validate(self):
        for r in self:

            livreur = r.env['res.partner'].search([('pin_livreur', '=', r.pin_livreur)],limit=1)
            if livreur:
                if r.pin == r.partner_id.pin:
                    r.picking_id.nbr_colis = r.nbr_colis
                    r.picking_id.custumer_note = r.custumer_note
                    r.picking_id.reception_type = r.reception_type
                    r.picking_id.confirmite = r.confirmite
                    r.picking_id.motif = r.motif
                    r.picking_id.action = r.action
                    r.picking_id.signature = r.signature
                    r.picking_id.livreur = livreur.id
                    if r.picking_id.reception_type == 'conforme':
                        r.picking_id.state = 'emarge'
                    else:
                        r.picking_id.state = 'retour'
                        user_ids = self.env["res.users"].search([])
                        for u in user_ids:
                            if u.has_group('stock.group_stock_manager'):
                                if r.action == 'rw':
                                    activity = r.env['mail.activity'].sudo(u.id).create({
                                        'activity_type_id': r.env.ref('alb_delivery_sign.mail_act_reception_partiel').id,
                                        'note': 'Retour',
                                        'res_id': r.picking_id.id,
                                        'res_model_id': self.env.ref('stock.model_stock_picking').id,
                                    })
                                else:
                                    activity = r.env['mail.activity'].sudo(u.id).create({
                                        'activity_type_id': r.env.ref(
                                            'alb_delivery_sign.mail_act_reception_partiel2').id,
                                        'note': 'Retour',
                                        'res_id': r.picking_id.id,
                                        'res_model_id': self.env.ref('stock.model_stock_picking').id,
                                    })
                else:
                    raise ValidationError(_('Le PIN du client est incorrect'))
            else:
                raise ValidationError(_('Le PIN du livreur est incorrect'))

class AlbMotif(models.Model):
    _name = 'alb.motif'
    _description = "Motif"

    name = fields.Char(string="Raison")