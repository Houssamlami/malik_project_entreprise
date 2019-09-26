# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, exceptions, _, tools
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import *
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning
                

class AccountInvoiceLine(models.Model):

    _inherit = 'account.invoice.line'
    
    
    colis = fields.Float(string="Colis", readonly=True, compute='get_colis_invoice_line')
    
    @api.multi
    def get_colis_invoice_line(self):
        for line in self:
            print('iiiiiiiiiiiii')
            if line.invoice_id.ref_livraison.state == 'done' and line.invoice_id.type not in ('in_invoice','in_refund'):
                move = line.invoice_id.ref_livraison
                line.colis = move.move_lines.filtered(lambda s: s.product_id.id == line.product_id.id).secondary_uom_qty
        