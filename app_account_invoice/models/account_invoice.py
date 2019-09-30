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
    qty_livrer_colis = fields.Float(string="Colis", readonly=True)
    commercial = fields.Many2one(comodel_name='hr.employee', string="Commercial")
    vendeur = fields.Many2one(comodel_name='hr.employee', string="Vendeur")
    object = fields.Text(string="Objet")
    ref_livraison = fields.Many2one(comodel_name='stock.picking', string="Ref livraison")
    
    
    
    @api.onchange('fac_charcuterie_f','fac_volaille_f')
    def onchange_fac_volaille_volaille(self):
        for record in self:
            if record.fac_charcuterie_f == True:
                account = self.env['account.account'].search([('code','=','411100')])
                record.account_id = account.id
                
            if record.fac_volaille_f == True:
                account = self.env['account.account'].search([('code','=','411101')])
                record.account_id = account.id
                
    @api.multi
    def recompute_qty_transport(self):
        for line in self:
            object = self.env['account.invoice.line']
            product = self.env['product.template'].search([('name', '=', 'TRANSPORT GRAND COMPTE')])
            productorigine = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
            dict = 0
            p = self.env['account.invoice.line'].search([('product_id', '=', productorigine.id),('invoice_id','=',line.id)])
            if len(p) == 0:
                for lines in line.invoice_line_ids:
                    if lines.product_id:
                        dict += lines.quantity
                object_create = object.create({
                'product_id': productorigine.id,
                'quantity': dict,
                'product_uom': product.uom_id.id,
                'account_id': self.env['account.account'].search([('code', '=', '707100')]).id,
                'invoice_id':line.id,
                'name':product.name,
                'price_unit':product.list_price,
                })
            else:
                dict = 0
                product_already_exist = self.env['account.invoice.line'].search([('product_id', '=', productorigine.id),('invoice_id','=',line.id)])
                for lines in line.invoice_line_ids:
                    if lines.product_id and (lines.product_id.name != 'TRANSPORT GRAND COMPTE'):
                        dict += lines.quantity
                object_create = product_already_exist.write({
                'product_id': productorigine.id,
                'quantity': dict,
                'product_uom': product.uom_id.id,
                'invoice_id':line.id,
                'account_id': self.env['account.account'].search([('code', '=', '707100')]).id,
                'name':product.name,
                'price_unit':product.list_price,
                })
                
                
    @api.multi
    def action_invoice_open(self):
        for invoice in self:
            if not invoice.date_due and invoice.type in ('out_invoice','out_refund'):
                raise exceptions.ValidationError(_('Date echeance !'))
                return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }    
            if ((invoice.fac_charcuterie_f and invoice.fac_volaille_f) or (not invoice.fac_charcuterie_f and not invoice.fac_volaille_f)) and invoice.type in ('out_invoice','out_refund'):
                raise exceptions.ValidationError(_('Merci de specifier le type Facture(Volaille ou chartuterie) !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
            if ((invoice.cli_gc and invoice.cli_pc) or (not invoice.cli_gc and not invoice.cli_pc)) and invoice.type in ('out_invoice','out_refund'):
                raise exceptions.ValidationError(_('Merci de specifier le type Facture(Grand ou petit compte) !'))
                return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
        return super(AccountInvoice, self).action_invoice_open()
    
                
class AccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"
    
    
    date_livraison = fields.Date(string='Date Livraison', readonly=True)
    
    
    def _select(self):
        select_str = """
            SELECT sub.id, sub.date,sub.date_livraison, sub.product_id, sub.partner_id, sub.country_id, sub.account_analytic_id,
                sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
                sub.fiscal_position_id, sub.user_id, sub.company_id, sub.nbr, sub.type, sub.state,
                sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,
                sub.product_qty, sub.price_total as price_total, sub.price_average as price_average,
                COALESCE(cr.rate, 1) as currency_rate, sub.residual as residual, sub.commercial_partner_id as commercial_partner_id
        """
        return select_str
    
    
    def _sub_select(self):
        select_str = """
                SELECT ail.id AS id,
                    ai.date_invoice AS date,
                    ai.date_livraison AS date_livraison,
                    ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
                    u2.name AS uom_name,
                    ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id,
                    1 AS nbr,
                    ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                    ai.partner_bank_id,
                    SUM ((invoice_type.sign_qty * ail.quantity) / u.factor * u2.factor) AS product_qty,
                    SUM(ail.price_subtotal_signed * invoice_type.sign) AS price_total,
                    SUM(ABS(ail.price_subtotal_signed)) / CASE
                            WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN SUM(ail.quantity / u.factor * u2.factor)
                               ELSE 1::numeric
                            END AS price_average,
                    ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                    count(*) * invoice_type.sign AS residual,
                    ai.commercial_partner_id as commercial_partner_id,
                    coalesce(partner.country_id, partner_ai.country_id) AS country_id
        """
        return select_str
            