# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, exceptions, _
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import datetime
import time
from datetime import *
from datetime import timedelta, datetime
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError


class CrmTeam(models.Model):
    _inherit = "crm.team"

    vendeur = fields.Many2one(comodel_name='hr.employee')
    name = fields.Char(string="Arrondissement/Secteur", required=True)
    
    
class BlockageBlockage(models.Model):
    _name = "blockage.blockage"
    
    name = fields.Char(string='Name')


class ResPartner(models.Model):
    _inherit = "res.partner"
    
    
    @api.model
    def create(self, vals):
        if vals.get('customer') and vals.get('phone'):
            seq = self.env['ir.sequence'].next_by_code('res.partner') or '/'
            vals['ref'] = seq
        if vals.get('customer') and vals.get('phone'):
            partner = self.env['res.partner'].search([('ref', '=', vals['ref'])], limit=1)
            if partner.ref == vals['ref']:
                raise exceptions.ValidationError(_('Reference client en double !'))
                return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }    
        result = super(ResPartner,self).create(vals) 
        return result
    
    
    def get_manager_canal_arond(self):
        for res in self:
            res.user_id = self.env['hr.employee'].search([('user_id', '=', res.team_id.user_id.id)],limit=1)
    
      

    user_id = fields.Many2one(comodel_name='hr.employee', compute='get_manager_canal_arond', track_visibility='onchange', string='Commercial')
    vendeur = fields.Many2one(comodel_name='hr.employee',related='team_id.vendeur', track_visibility='onchange', string='Vendeur')
    vendeur_commarcial = fields.Many2one(comodel_name='res.users', string="", track_visibility='onchange')
    Client_Volaille = fields.Boolean('Client Volailles', track_visibility='onchange')
    Client_Charcuterie =  fields.Boolean('Client Charcuterie', track_visibility='onchange')
    Client_GC = fields.Boolean(string='Client Gros Compte', track_visibility='onchange')
    Client_PC = fields.Boolean(string='Client Petit Compte', track_visibility='onchange')
    commercial_id = fields.Many2one(comodel_name='hr.employee', string="Commercial", related='user_id', store=True)
    client_gc_pc = fields.Selection([('client_gros_compte', 'Client gros compte'),('client_petit_compte', 'Client petit compte')],string="Type de client")
    vat = fields.Char(string='VAT', track_visibility='onchange')
    pricelist_for_regroupby = fields.Many2one(comodel_name='product.pricelist',related='property_product_pricelist', store=True)
    Bolocagettm = fields.Many2one(comodel_name='blockage.blockage', track_visibility='onchange')
    blocagex_limite_nbr_fac=fields.Boolean('Blocage par Nombre de facture')
    limite_nbr_fac=fields.Integer('limite Nombre de facture', track_visibility='onchange')
    nbr_fac_ouverte=fields.Integer('Nombre de facture ouvertes',compute='_on_calcule_factures')
    blocagex_limite_credit=fields.Boolean('Blocage par limite de credit', track_visibility='onchange')
    bloque_vo = fields.Boolean(string='Blocage volaille', compute='_on_change_credit',store=True)
    bloque_ch = fields.Boolean(string='Blocage charcuterie', compute='_on_change_credit',store=True)
    bloque=fields.Boolean('bloque',compute='_on_change_credit',store=True)
    blocagex_limite_credit_charcuterie=fields.Boolean('Blocage par limite de credit charcuterie', track_visibility='onchange')
    blocagex_echeance_facture_charcuterie=fields.Boolean('Blocage par echeance charcuterie', track_visibility='onchange')
    limite_nbr_fac_charcuterie=fields.Integer('limite Nombre de facture charcuterie', track_visibility='onchange')
    date_facture_charcuterie=fields.Date('Date de la facture charcuterie impayante',compute='_on_calcule_factures')
    nbr_fac_ouverte_charcuterie=fields.Integer('Nombre de facture ouvertes',compute='_on_calcule_factures')
    nbr_jours_decheance_charcuterie=fields.Integer('Compteur des jours',compute='_on_calcule_factures')
    limite_credit_charcuterie=fields.Float('limite credit charcuterie', track_visibility='onchange')
    limite_credit_volaille=fields.Float('limite credit  volaille', track_visibility='onchange')
    credit_charcuterie=fields.Float('Credit charcuterie',compute='_on_calcule_factures')
    credit_volaille=fields.Float('Credit volaille',compute='_on_calcule_factures')
    date_lyuoMa = fields.Date(string='today', default=date.today())
    debloque_exce_ch = fields.Boolean(string=u"Déblocage exceptionnel charcuterie", compute='onchange_debloque_exce')
    debloque_exce_vo = fields.Boolean(string=u"Déblocage exceptionnel volaille", compute='onchange_debloque_exce')
    date_reblockage = fields.Date(string='Date de reblocage')
#     champs inactive est un champs rempli par l utilisateur c est le nobre des jours qui controle l etat de client si actif ou pas par exemple si le champs inactive st 30 jours cv si le champs diff_time est moins que 30 jours le client est en etat active sinon le client est en etat non actif
    Inactive = fields.Integer('Nbr de jours d inactivité')
# champs diff_time est le nombre de jours entre la date de system (to_day) et la date de la dernier commande (date_last_commande)
    diff_time= fields.Integer('Nbr de jours passés sans commander')
    Etat= fields.Boolean('Client Actif')
    date_last_commande=  fields.Datetime('Date de la derniere commande', compute='last_command')
    date_lyuoM = fields.Datetime(string='today', default=datetime.today())
    echeance_charcuterie_par_jour=fields.Integer('Limite echeance charcuterie par jour')
    ref = fields.Char(string='Reference interne', track_visibility='onchange')
    customer_cmd_ceiling = fields.Float('Plafond commande client', track_visibility='onchange')
    customer_cmd_ceiling_cha = fields.Float('Plafond commande charcuterie', track_visibility='onchange')
    customer_cmd_ceiling_vol = fields.Float('Plafond commande volaille', track_visibility='onchange')
    
    @api.onchange('debloque_exce_ch','debloque_exce_vo')
    def onchange_debloque_exce(self):
        for record in self:
            if record.debloque_exce_ch ==True:
                record.bloque_ch=False
                record.bloque=False
            if record.debloque_exce_vo ==True:
                record.bloque_vo=False
                record.bloque=False 
    
    _sql_constraints = [
        ('ref_unique_part', 'unique(ref)', 'La reference client doit etre unique!'),
    ]
    
    
    @api.one
    def last_command(self):
        for partners in self:
            date_last_commande = 0
            if partners.id :
                productbl = self.env['sale.order'].search([
                ('partner_id', '=', self.id)], order='id desc', limit=1)
                date_last_commande = productbl.create_date
            partners.date_last_commande = date_last_commande
            # partners.user_id=vendeur_commarcial

    @api.one
    def _on_calcule_factures(self):
        for record in self:
            credit_charcuterie=0
            nbr_fac_ouverte_charcuterie=0
            nbr_fac_ouverte=0
            credit_volaille=0
            date_facture_charcuterie=0
            nbr_jours_decheance_charcuterie=0
            DATETIME_FORMAT = "%Y-%m-%d"
            if record.Client_Volaille==True and record.Client_Charcuterie==True :
                productbl = self.env['account.invoice'].search([('partner_id', '=', self.id),('state', 'like', 'open'),('fac_charcuterie_f', '=', True)])
                for line in productbl:
                    nbr_fac_ouverte_charcuterie=len(line)
                    credit_charcuterie += line.residual_company_signed
                    date_facture_charcuterie=min(line).date_invoice
                    nbr_jours_decheance_charcuterie=abs((datetime.strptime(date_facture_charcuterie, DATETIME_FORMAT)- datetime.strptime(fields.Date.context_today(self), DATETIME_FORMAT)).days)
                record.credit_charcuterie = credit_charcuterie
                record.nbr_fac_ouverte_charcuterie=nbr_fac_ouverte_charcuterie
                record.date_facture_charcuterie=date_facture_charcuterie
                record.nbr_jours_decheance_charcuterie=nbr_jours_decheance_charcuterie
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
                    date_facture_charcuterie=min(line).date_invoice
                    nbr_jours_decheance_charcuterie=abs((datetime.strptime(date_facture_charcuterie, DATETIME_FORMAT)- datetime.strptime(fields.Date.context_today(self), DATETIME_FORMAT)).days)
                record.credit_charcuterie = credit_charcuterie
                record.nbr_fac_ouverte_charcuterie=nbr_fac_ouverte_charcuterie            
                record.date_facture_charcuterie=date_facture_charcuterie
                record.nbr_jours_decheance_charcuterie=nbr_jours_decheance_charcuterie         
                
                
    @api.model
    def fields_get(self, fields=None):
        fields_to_hide = ['user_id','vendeur_commarcial']
        res = super(ResPartner, self).fields_get()
        for field in fields_to_hide:
            res[field]['selectable'] = False
        return res   


    @api.depends('credit','credit_limit','credit_charcuterie','limite_nbr_fac','limite_credit_charcuterie','nbr_fac_ouverte','limite_nbr_fac_charcuterie','nbr_fac_ouverte_charcuterie','nbr_jours_decheance_charcuterie','echeance_charcuterie_par_jour')
    def _on_change_credit(self):
        for record in self:
            if record.blocagex_limite_credit:
                if record.credit_volaille > record.credit_limit:
                    record.bloque_vo=True
                    record.bloque=True
            if record.blocagex_limite_nbr_fac:
                if record.nbr_fac_ouverte >= record.limite_nbr_fac:
                    record.bloque_vo=True
                    record.bloque=True
            if record.blocagex_limite_credit_charcuterie:
                if record.credit_charcuterie > record.limite_credit_charcuterie:
                    record.bloque_ch=True
                    record.bloque=True
            if record.blocagex_echeance_facture_charcuterie:
                if record.nbr_jours_decheance_charcuterie > record.echeance_charcuterie_par_jour:
                    record.bloque_ch=True
                    record.bloque=True
    
    
    @api.onchange('Client_GC','Client_PC')
    def onchange_Client_PC_Client_GC(self):
        if self.Client_GC:
            self.client_gc_pc = 'client_gros_compte'
        else:
            self.client_gc_pc = 'client_petit_compte'  
        
        
    @api.onchange('team_id')
    def onchange_get_default(self):
        for partner in self:
            if partner.team_id :
                team = partner.team_id
                employee = self.env['hr.employee'].search([('user_id', '=', team.user_id.id)])
                partner.user_id = employee


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