# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError




class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    
    
    charcuterie = fields.Boolean(string="Charcuterie", default=False)
    volaille = fields.Boolean(string="Volaille", default=False)
    note_payment = fields.Text(string="Remarque")
    amount_charcuterie = fields.Float(string="Montant Charcuterie")
    amount_volaille = fields.Float(string="Montant Volaille")
    
    
    @api.one
    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if self.invoice_ids:
            self.destination_account_id = self.invoice_ids[0].account_id.id
        elif self.payment_type == 'transfer':
            if not self.company_id.transfer_account_id.id:
                raise UserError(_('Transfer account not defined on the company.'))
            self.destination_account_id = self.company_id.transfer_account_id.id
        elif self.partner_id:
            if self.partner_type == 'customer' and self.charcuterie == True and self.volaille == False:
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            elif self.partner_type == 'customer' and self.charcuterie == False and self.volaille == True:
                self.destination_account_id = self.env['account.account'].search([('code','=','411101')]).id
            elif self.partner_type == 'customer' and self.charcuterie == False and self.volaille == False:
                self.destination_account_id = self.partner_id.property_account_receivable_id.id
            else:
                self.destination_account_id = self.partner_id.property_account_payable_id.id
        elif self.partner_type == 'customer':
            default_account = self.env['ir.property'].get('property_account_receivable_id', 'res.partner')
            self.destination_account_id = default_account.id
        elif self.partner_type == 'supplier':
            default_account = self.env['ir.property'].get('property_account_payable_id', 'res.partner')
            self.destination_account_id = default_account.id
