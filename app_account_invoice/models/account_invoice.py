# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, exceptions, _, tools
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import *
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning
                

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'
            
    fac_charcuterie_f = fields.Boolean('Charcuterie')
    fac_volaille_f = fields.Boolean('Volaille')
    cli_gc = fields.Boolean('Client Gros compte', related='partner_id.Client_GC')
    cli_pc = fields.Boolean('Client petit compte', related='partner_id.Client_PC')
    date_commande = fields.Date(string="Date Commande")
    date_livraison = fields.Date(string="Date Livraison")
    
    @api.onchange('fac_charcuterie_f','fac_volaille_f')
    def onchange_fac_volaille_volaille(self):
        for record in self:
            if record.fac_charcuterie_f == True:
                account = self.env['account.account'].search([('code','=','411100')])
                record.account_id = account.id
                
            if record.fac_volaille_f == True:
                account = self.env['account.account'].search([('code','=','411101')])
                record.account_id = account.id
            