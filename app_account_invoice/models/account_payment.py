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