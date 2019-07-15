# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, exceptions, _
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    vendeur = fields.Many2one(comodel_name='res.partner')
    
    
class BlockageBlockage(models.Model):
    _name = "blockage.blockage"
    
    name = fields.Char(string='Name')


class ResPartner(models.Model):
    _inherit = "res.partner"

    user_id = fields.Many2one(comodel_name='res.users',required=True)
    vendeur = fields.Many2one('res.partner',related='team_id.vendeur',required=True)
    vendeur_commarcial = fields.Many2one(comodel_name='res.users', string="Commercial")
    Client_Volaille =  fields.Boolean('Client Volailles')
    Client_Charcuterie =  fields.Boolean('Client Charcuterie')
    Client_GC =  fields.Boolean('Client Gros Compte')
    Client_PC =  fields.Boolean('Client Petit Compte')
    client_gc_pc = fields.Selection([('client_gros_compte', 'Client gros compte'),('client_petit_compte', 'Client petit compte')],string="Type de client")
    vat = fields.Char('VAT',required=True)
    pricelist_for_regroupby = fields.Many2one(comodel_name='product.pricelist',related='property_product_pricelist', store=True)
    Bolocagettm = fields.Many2one(comodel_name='blockage.blockage')
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
    
    
    @api.onchange('Client_GC','Client_PC')
    def onchange_Client_PC_Client_GC(self):
        if self.Client_GC:
            self.client_gc_pc = 'client_gros_compte'
        else:
            self.client_gc_pc = 'client_petit_compte'  
        
        
    @api.onchange('team_id')
    def onchange_get_default(self):
        for partners in self:
            vendeur_commarcial = 0
            team = 0
            if partners.team_id :
                team=partners.team_id.id
                productbl = self.env['res.users'].search([
                ('sale_team_id', '=', team)])
                partners.user_id = productbl.id


    @api.onchange('vat')
    def onchange_get_tva_default(self):
        for partners in self:
            if partners.vat :
                productbl = self.env['res.partner'].search([
                ('vat', 'like', partners.vat)], limit=1)
                if productbl.vat == partners.vat:
                    raise exceptions.ValidationError(_('Vous avez déjà saisi un Client avec le meme code de TVA, merci de changer le code TVA !'))
                    return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                    }		