# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, exceptions, _, tools
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import *
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning
                

class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'
    
    
    colis = fields.Float(string="Colis", readonly=True, compute='get_colis_invoice_line', store=True)
    
    @api.multi
    @api.depends('invoice_id.ref_livraison')
    def get_colis_invoice_line(self):
        for line in self:
            print('iiiiiiiiiiiii')
            if line.invoice_id.ref_livraison.state in ('done','emarge') and line.invoice_id.type not in ('in_invoice','in_refund'):
                move = line.invoice_id.picking_ids.filtered(lambda s: s.picking_type_code == 'outgoing' and s.state in ('done','emarge'))
                print(move)
                move_return = self.env['stock.picking'].search([('state', '=', 'done'),('group_id','=',line.invoice_id.ref_livraison.group_id.id),('picking_type_id.code', '=', 'incoming')])
                cmpt = 0
                cmt = 0   
                move_lines = (move_out.move_lines.filtered(lambda s: s.product_id.id == line.product_id.id) for move_out in move)
                moves_lines_return = (moves_in.move_lines.filtered(lambda s: s.product_id.id == line.product_id.id) for moves_in in move_return)
                for lines in move_lines:
                    for l in lines:
                        cmpt += l.secondary_uom_qty
                    print(cmpt)
                for lines_return in moves_lines_return:
                    cmt = lines_return.secondary_uom_qty
                    print(cmt)
                line.colis = cmpt - cmt