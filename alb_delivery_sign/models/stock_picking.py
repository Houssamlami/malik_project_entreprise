# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'mail.thread', 'mail.activity.mixin']

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
            ('rw,', 'Retour à l’entrepôt'),
            ('rwd', 'Retour à l’entrepôt et re-livraison'),
            ('rwdr','Retour à l’entrepôt et remise en stock'),
        ],
        string='Action'
    )

    def customer_reception(self):
        action = self.env.ref('alb_delivery_sign.action_custumer_reception').read()[0]
        action['context'] = {'default_picking_id': self.id}
        action['views'] = [(self.env.ref('alb_delivery_sign.custumer_reception_wizard').id, 'form')]
        return action

    def activity_update(self):
        to_clean, to_do = self.env['stock.picking'], self.env['stock.picking']
        for r in self:
            user_ids = self.env["res.users"].search([])
            for u in user_ids:
                if u.has_group('stock.group_stock_manager'):
                    if r.state in ['emarge', 'retour']:
                        r.activity_schedule(
                            'alb_delivery_sign.mail_act_reception_partiel',
                            user_id=r.id)
                    else:
                        to_clean |= r
                else:
                    pass
        if to_clean:
            to_clean.activity_unlink(['alb_delivery_sign.mail_act_reception_partiel', ])
        if to_do:
            to_do.activity_feedback(['alb_delivery_sign.mail_act_reception_partiel', ])


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'


    # @api.model
    # def default_get(self, fields):
    #     if len(self.env.context.get('active_ids', list())) > 1:
    #         raise UserError("You may only return one picking at a time!")
    #     res = super(ReturnPicking, self).default_get(fields)
    #
    #     move_dest_exists = False
    #     product_return_moves = []
    #     picking = self.env['stock.picking'].browse(self.env.context.get('active_id'))
    #     if picking:
    #         res.update({'picking_id': picking.id})
    #         if not picking.state in ['done', 'emarge', 'retour']:
    #             raise UserError(_("You may only return Done pickings"))
    #         for move in picking.move_lines:
    #             if move.state == 'cancel':
    #                 continue
    #             if move.scrapped:
    #                 continue
    #             if move.move_dest_ids:
    #                 move_dest_exists = True
    #             quantity = move.product_qty - sum(move.move_dest_ids.filtered(lambda m: m.state in ['partially_available', 'assigned', 'done']).\
    #                                               mapped('move_line_ids').mapped('product_qty'))
    #             quantity = float_round(quantity, precision_rounding=move.product_uom.rounding)
    #             product_return_moves.append((0, 0, {'product_id': move.product_id.id, 'quantity': quantity, 'move_id': move.id, 'uom_id': move.product_id.uom_id.id}))
    #
    #         if not product_return_moves:
    #             raise UserError(_("No products to return (only lines in Done state and not fully returned yet can be returned)!"))
    #         if 'product_return_moves' in fields:
    #             res.update({'product_return_moves': product_return_moves})
    #         if 'move_dest_exists' in fields:
    #             res.update({'move_dest_exists': move_dest_exists})
    #         if 'parent_location_id' in fields and picking.location_id.usage == 'internal':
    #             res.update({'parent_location_id': picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.view_location_id.id or picking.location_id.location_id.id})
    #         if 'original_location_id' in fields:
    #             res.update({'original_location_id': picking.location_id.id})
    #         if 'location_id' in fields:
    #             location_id = picking.location_id.id
    #             if picking.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
    #                 location_id = picking.picking_type_id.return_picking_type_id.default_location_dest_id.id
    #             res['location_id'] = location_id
    #     return res
