# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api, exceptions, _, tools
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from datetime import *
from datetime import date
from odoo.exceptions import except_orm, Warning, RedirectWarning
                

class AccountInvoice(models.Model):

    _inherit = 'account.invoice'
            
    fac_charcuterie_f = fields.Boolean('Charcuterie', track_visibility='onchange')
    fac_volaille_f = fields.Boolean('Volaille', track_visibility='onchange')
    cli_gc = fields.Boolean('Client Gros compte', related='partner_id.Client_GC', track_visibility='onchange', store=True)
    cli_pc = fields.Boolean('Client petit compte', related='partner_id.Client_PC', track_visibility='onchange', store=True)
    date_commande = fields.Date(string="Date Commande")
    date_livraison = fields.Date(string="Date Livraison")
    qty_livrer_colis = fields.Float(string="Colis", readonly=True, compute='get_total_colis_invoice')
    commercial = fields.Many2one(comodel_name='hr.employee', string="Commercial", track_visibility='onchange')
    vendeur = fields.Many2one(comodel_name='hr.employee', string="Vendeur", track_visibility='onchange')
    object = fields.Text(string="Objet")
    grosiste = fields.Boolean(string='Grossiste', track_visibility='onchange')
    ref_livraison = fields.Many2one(comodel_name='stock.picking', string="Ref livraison", track_visibility='onchange')
    
    def get_total_colis_invoice(self):
        for record in self:
            colis = sum(self.env['stock.picking'].search([('state', '=', 'done'),('picking_type_id.code', '=', 'outgoing'),('origin', 'ilike', self.origin)]).mapped('total_colis_delivered')) - self.picking_ids.filtered(lambda r: r.picking_type_id.code == 'incoming' and r.state == 'done').total_colis_delivered
            record.qty_livrer_colis = colis
    
    
    
    '''@api.onchange('fac_charcuterie_f','fac_volaille_f')
    def onchange_fac_volaille_volaille(self):
        for record in self:
            if record.fac_charcuterie_f == True:
                account = self.env['account.account'].search([('code','=','411100')])
                record.account_id = account.id
                
            if record.fac_volaille_f == True:
                account = self.env['account.account'].search([('code','=','411101')])
                record.account_id = account.id'''
                
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
                'account_id': self.env['account.account'].search([('code', '=', '706003')]).id,
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
                'account_id': self.env['account.account'].search([('code', '=', '706003')]).id,
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
    fac_charcuterie_f = fields.Boolean('Charcuterie', readonly=True)
    fac_volaille_f = fields.Boolean('Volaille', readonly=True)
    cli_gc = fields.Boolean('Client Gros compte', readonly=True)
    cli_pc = fields.Boolean('Client petit compte', readonly=True)
    commercial = fields.Many2one(comodel_name='hr.employee', string="Commercial", readonly=True)
    vendeur = fields.Many2one(comodel_name='hr.employee', string="Vendeur", readonly=True)
    team_id = fields.Many2one('crm.team', string='Sales Channel')
    ref_invoice_name = fields.Char('Référence', readonly=True)
    type_avoir = fields.Selection([
        ('Qualité de Produit BONA', 'Qualité de Produit BONA'),
        ('Qualité de Produit Crusvi', 'Qualité de Produit Crusvi'),
        ('Qualité de Produit Imex', 'Qualité de Produit Imex'),
        ('Qualité de Produit Atlas negoce', 'Qualité de Produit Atlas negoce'),
        ('Qualité de Produit Nouvelle Atlas', 'Qualité de Produit Nouvelle Atlas'),
        ('Qualité de Produit Tradco', 'Qualité de Produit Tradco'),
        ('Refus de commandes', 'Refus de commandes'),
        ('Manque de produit à la livraison', 'Manque de produit à la livraison'),
        ('Erreur de préparation TTM', 'Erreur de préparation TTM'),
        ('Annulation de facture et refacturation', 'Annulation de facture et refacturation'),
        ('DLC Courte', 'DLC Courte'),
        ('Erreur de saisie', 'Erreur de saisie'),
        ('Gonflement par commercial', 'Gonflement par commercial'),
        ('Erreur sur la remise', 'Erreur sur la remise'),
        ('Erreur sur le prix', 'Erreur sur le prix'),
        ('Geste commercial', 'Geste commercial'),
        ], readonly=True)
    grosiste = fields.Boolean(string='Grossiste', readonly=True)
    
    
    def _select(self):
        select_str = """
            SELECT sub.id, sub.date,sub.date_livraison, sub.type_avoir, sub.grosiste, sub.ref_invoice_name, sub.team_id as team_id, sub.fac_volaille_f, sub.fac_charcuterie_f, sub.cli_gc, sub.cli_pc, sub.product_id, sub.partner_id, 
                sub.country_id, sub.account_analytic_id, sub.commercial, sub.vendeur, sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
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
                    ai.team_id as team_id,
                    ai.fac_charcuterie_f AS fac_charcuterie_f,
                    ai.fac_volaille_f AS fac_volaille_f,
                    ai.cli_pc AS cli_pc,
                    ai.grosiste AS grosiste,
                    ai.number AS ref_invoice_name,
                    ai.type_avoir AS type_avoir,
                    ai.cli_gc AS cli_gc,
                    ai.commercial AS commercial,
                    ai.vendeur AS vendeur,
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
    
    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", ai.team_id, ai.type_avoir"
            