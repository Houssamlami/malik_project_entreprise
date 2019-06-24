# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, exceptions, _, tools
import datetime
import time
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import *
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from datetime import date
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError

class Respartner(models.Model):

    _inherit = 'res.partner'

    blocagex_limite_nbr_fac=fields.Boolean('Blocage par Nombre de facture')
    limite_nbr_fac=fields.Integer('limite Nombre de facture')
    nbr_fac_ouverte=fields.Integer('Nombre de facture ouvertes',compute='_on_calcule_factures')
    blocagex_limite_credit=fields.Boolean('Blocage par limite de credit')
    bloque=fields.Boolean('bloque',compute='_on_change_credit',store=True)
    blocagex_limite_credit_charcuterie=fields.Boolean('Blocage par limite de credit charcuterie')
    limite_nbr_fac_charcuterie=fields.Integer('limite Nombre de facture charcuterie')
    nbr_fac_ouverte_charcuterie=fields.Integer('Nombre de facture ouvertes',compute='_on_calcule_factures')
    limite_credit_charcuterie=fields.Float('limite credit charcuterie')
    limite_credit_volaille=fields.Float('limite credit  volaille')
    credit_charcuterie=fields.Float('Credit charcuterie',compute='_on_calcule_factures')
    credit_volaille=fields.Float('Credit volaille',compute='_on_calcule_factures')

    @api.one
    def _on_calcule_factures(self):
        for record in self:
            credit_charcuterie=0
            nbr_fac_ouverte_charcuterie=0
            nbr_fac_ouverte=0
            credit_volaille=0
            if record.Client_Volaille==True and record.Client_Charcuterie==True :
                productbl = self.env['account.invoice'].search([('partner_id', '=', self.id),('state', 'like', 'open'),('fac_charcuterie_f', '=', True)])
                for line in productbl:
                    nbr_fac_ouverte_charcuterie=len(line)
                    credit_charcuterie += line.residual_company_signed
                record.credit_charcuterie = credit_charcuterie
                record.nbr_fac_ouverte_charcuterie=nbr_fac_ouverte_charcuterie
                productblv = self.env['account.invoice'].search([('partner_id', '=', self.id),('state', 'like', 'open'),('fac_volaille_f', '=', True)])
                for linev in productblv:
                    nbr_fac_ouverte=len(linev)
                    credit_volaille += linev.residual_company_signed
                record.credit_volaille = credit_volaille
                record.nbr_fac_ouverte=nbr_fac_ouverte
            if record.Client_Volaille==True and record.Client_Charcuterie==False :
                productblv = self.env['account.invoice'].search([('partner_id', '=', self.id),('state', 'like', 'open'),('fac_volaille_f', '=', True)])
                for linev in productblv:
                    nbr_fac_ouverte=len(linev)
                    credit_volaille += linev.residual_company_signed
                record.credit_volaille = credit_volaille
                record.nbr_fac_ouverte=nbr_fac_ouverte
            if record.Client_Volaille==False and record.Client_Charcuterie==True :
                productbl = self.env['account.invoice'].search([('partner_id', '=', self.id),('state', 'like', 'open'),('fac_charcuterie_f', '=', True)])
                for line in productbl:
                    nbr_fac_ouverte_charcuterie=len(line)
                    credit_charcuterie += line.residual_company_signed
                record.credit_charcuterie = credit_charcuterie
                record.nbr_fac_ouverte_charcuterie=nbr_fac_ouverte_charcuterie			


    @api.depends('credit','limite_credit_volaille','credit_charcuterie','limite_nbr_fac','limite_credit_charcuterie','nbr_fac_ouverte','limite_nbr_fac_charcuterie','nbr_fac_ouverte_charcuterie')
    def _on_change_credit(self):
        for record in self:
            if record.blocagex_limite_credit:
                if record.credit_volaille > record.limite_credit_volaille:
                    record.bloque=True
            if record.blocagex_limite_nbr_fac:
                if record.nbr_fac_ouverte >= record.limite_nbr_fac:
                    record.bloque=True
            if record.blocagex_limite_credit_charcuterie:
                if record.credit_charcuterie > record.limite_credit_charcuterie:
                    record.bloque=True
            if record.blocagex_limite_credit_charcuterie:
                if record.nbr_fac_ouverte_charcuterie >= record.limite_nbr_fac_charcuterie:
                    record.bloque=True


class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'
    
''' 
    def _compute_diff_qty_delivred_ordred(self):
        for line in self:
            diff_qty = 0
            if line.product_id:
                diff_qty = line.product_uom_qty-line.qty_delivered
            if diff_qty < 0.0:
                diff_qty = diff_qty*(-1)
                
            line.diff_cmd_deli_qty = diff_qty
            
    @api.onchange('qty_delivered')
    def on_change_qty_delivered_delv(self):
        self._compute_diff_qty_delivred_ordred()
                
                
    diff_cmd_deli_qty = fields.Float(string=u"Différence Quantité", compute='_compute_diff_qty_delivred_ordred')  

'''

class SaleOrder(models.Model):

    _inherit = 'sale.order'         
     
                
    '''@api.depends('order_line')
    def _get_ecart_qty(self):
        for record in self:
            cmpt = 0.0
            for line in record.order_line:
                if line.product_id:
                    cmpt += line.diff_cmd_deli_qty
            record.ecart_qty_kg = cmpt
           #record.update({
                #'ecart_qty_kg':cmpt
               # })
               
    @api.onchange('order_line')
    def on_change_order_line_diff_cmd_deli_qty(self):
        for record in self:
            record._get_ecart_qty()
    '''              
            
    test_bloque = fields.Char('Test bloque')
    fac_charcuterie_volaille = fields.Selection([('charcuterie', 'Charcuterie'),('volaille', 'Volaille')],string="Type de commande")
    client_gc_pc = fields.Selection('Type Client', related='partner_id.client_gc_pc', store=True)
    #ecart_qty_kg = fields.Float(string='Ecart qty (KG)', compute='_get_ecart_qty', readonly=True, store=True)
    #ecart_qty_colis = fields.Float('Ecart qty (Colis)', compute=_get_ecart_qty, store=True)

    @api.onchange('partner_id')
    def on_change_statecr(self):
        for record in self:
            if record.partner_id.bloque:
                record.test_bloque="bloquer"
                raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
                }

    @api.onchange('product_id')
    def on_change_stateproduct(self):
        for record in self:
            if not record.fac_charcuterie_volaille:
                raise exceptions.ValidationError(_('Merci de Choisir le type de votre vente !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
                }
                
    
    @api.multi
    def _prepare_invoice(self):
        
        self.ensure_one()
        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))
        invoice_vals = {
            'name': self.client_order_ref or '',
            'origin': self.name,
            'type': 'out_invoice',
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'date_commande': self.date_order,
            'date_livraison': self.requested_date,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.user_id and self.user_id.id,
            'team_id': self.team_id.id,
            
        }
        return invoice_vals
                

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
            