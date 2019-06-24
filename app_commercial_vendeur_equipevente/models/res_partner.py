# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, exceptions, _
from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
from openerp.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError


# Record the net weight of the order line

class CrmTeam(models.Model):
    _inherit = "crm.team"

	
    vendeur = fields.Many2one('res.partner')

	
# class Tailleclient(models.Model):
    
    # _name = "taille.client"
	
	
    # name = fields.Char('Taille')

class ResPartner(models.Model):
    _inherit = "res.partner"

	

    # vendeurtest = fields.Many2one('res.users',related='team_id.user_id') c est le canal manager
    user_id = fields.Many2one('res.users',required=True)
    vendeur = fields.Many2one('res.partner',related='team_id.vendeur',required=True)
    vendeur_commarcial = fields.Many2one(comodel_name='res.users', string="Commercial")
    Client_Volaille =  fields.Boolean('Client Volailles')
    Client_Charcuterie =  fields.Boolean('Client Charcuterie')
    Client_GC =  fields.Boolean('Client Gros Compte')
    Client_PC =  fields.Boolean('Client Petit Compte')
    client_gc_pc = fields.Selection([('client_gros_compte', 'Client gros compte'),('client_petit_compte', 'Client petit compte')],string="Type de client")
    # Marchandises_client = fields.Many2one('marchandises.client')
    # Taille_client = fields.Many2one('taille.client')
    vat = fields.Char('VAT',required=True)
    pricelist_for_regroupby = fields.Many2one('product.pricelist',related='property_product_pricelist', store=True)
    
    
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
                # partners.vendeur_commarcial = productbl.id
                partners.user_id = productbl.id
            # partners.user_id=vendeur_commarcial
			
			
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
                
            # partners.user_id=vendeur_commarcial			
			
class SalesOrder(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

	
    vendeur = fields.Many2one(comodel_name='res.partner', string="Vendeur")
    user_id = fields.Many2one(comodel_name='res.users', string="Commercial")
	
    @api.onchange('partner_id')
    def onchange_get_default_ven(self):
        for partners in self:
            team = 0
            vendeur = 0
            user_id = 0
            if partners.partner_id :
                team=partners.partner_id.id
                productbl = self.env['res.partner'].search([
                ('id', '=', team)])
                vendeur = productbl.vendeur
                user_id = productbl.user_id
            partners.vendeur = vendeur
            partners.user_id = user_id
            # partners.user_id=vendeur_commarcial