# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, float_compare, float_round
from odoo import api, fields, exceptions, models, _
import datetime
from datetime import *


class SaleOrder(models.Model):
    _inherit = "sale.order"

    total_weight = fields.Float(string='Total Weight(kg)', compute='_compute_weight_total')
    total_colis = fields.Float(string='Total colis', compute='_compute_colis_total')
    total_colis_livrer = fields.Float(string='Total colis livrer', compute='_compute_colis_livrer_total')
    total_volume_ht = fields.Float(string='Montant Total TTC', compute='_compute_volumeht_total')
    total_ht = fields.Float(string='Montant Total HT', compute='_compute_ht_total')
    vendeur = fields.Many2one(comodel_name='hr.employee', string="Vendeur")
    user_id = fields.Many2one(comodel_name='hr.employee', string="Commercial", default=False)
    
    Bolocagettm = fields.Integer('blo')
    Bolocagettm_id = fields.Many2one(comodel_name='blockage.blockage')
    transport_id = fields.Many2one(comodel_name='blockage.blockage', related='Bolocagettm_id', store=True)
    total_weight_stock_char = fields.Float(string='Total charcuterie)', compute='_compute_weight_total_stock_char')
    total_weight_stock_srg = fields.Float(string='Total surgele)', compute='_compute_weight_total_stock_srg')
    total_weight_stock_vv = fields.Float(string='Total volaille)', compute='_compute_weight_total_stock_vv')
    total_weight_stock_agn = fields.Float(string='Total Agneaux', compute='_compute_weight_total_stock_agn')
    total_weight_stock_epc = fields.Float(string='Total epecerie', compute='_compute_weight_total_stock_epc')
    produitalivrer = fields.Char('Produit a livrer', compute='get_product_ttm')
    commercial_id = fields.Many2one(comodel_name='hr.employee', string="Commercial", related='user_id', store=True)
    Expediteur =  fields.Selection([('MV', 'Malik V'), ('An', 'Atlas N')])    
    zip_df =  fields.Char(string='CP', compute='get_default_zip')
    adresse_liv =  fields.Char(string='Adresse livraison', compute='get_default_zip')
    city =  fields.Char(string='Ville', compute='get_default_zip')    
    observation =  fields.Char(string='Observation')
    test_bloque = fields.Char('Information blockage')
    cmd_charcuterie = fields.Boolean(string="Charcuterie")
    cmd_volaille = fields.Boolean(string="Volaille")
    fac_charcuterie_volaille = fields.Selection([('charcuterie', 'Charcuterie'),('volaille', 'Volaille')],string="Type commande")
    client_gc_pc = fields.Selection('Type Client', related='partner_id.client_gc_pc', store=True)
    debloque_exce_vopp = fields.Boolean(string="Deblocage Exceptionnel")
    commande_type = fields.Selection([('commande_charc', 'Commande charcuterie'),('commande_volaille', 'Commande Volaille')], string="Type de commande")
    #ecart_qty_kg = fields.Float(string='Ecart qty (KG)', compute='_get_ecart_qty', readonly=True, store=True)
    #ecart_qty_colis = fields.Float('Ecart qty (Colis)', compute=_get_ecart_qty, store=True)
    refused_command = fields.Boolean(string="CMD Refusée", track_visibility='onchange')
    reason_refuse = fields.Selection([('relivraison', 'Relivraison'),('remet_en_stock', 'Remet en Stock '), ('detruit', 'Detruit')], track_visibility='onchange', string="Raison Refus")
    cmd_validated = fields.Boolean(string=u"CMD Validée gros compte", track_visibility='onchange')
    total_qty_ordred1 = fields.Float(string='Total qtyor', compute='_compute_colis_total_ordred')
    total_qty_delivred = fields.Float(string='Total delievred', compute='_compute_colis_total_delivred')
    total_qty_invoiced = fields.Float(string='Total invoiced', compute='_compute_colis_total_invoiced')
    etat_fac1 = fields.Char(string='Etat facture', compute='_compute_colis_total_etat')
    etat_fac1_copy = fields.Char(string='Etat facture copy', compute='_compute_colis_total_etat_copy',store=True)
    grand_compte = fields.Boolean(string='Commande Grand Compte', default= False)
    payment_term_id = fields.Many2one('account.payment.term', string='Conditions de règlement', oldname='payment_term', compute='onchange_payment_term_id_so')
    normal_cmd = fields.Boolean(string='Commande Normale', default=True, track_visibility='onchange')
    grosiste_cmd = fields.Boolean(string='Grossiste', track_visibility='onchange')
    bl_not_conform = fields.Boolean(string='BL Non Conforme', default=False, track_visibility='onchange')
    reason_no_conformity = fields.Selection([('colis_moins', 'Colis en moins'),('colis_plus', 'Colis en plus')], track_visibility='onchange', string="Raison")
    precise_no_conformity = fields.Selection([('non', 'Non'),('oui', 'Oui')], track_visibility='onchange', string="Précisé")
    detail_no_conformity = fields.Text(string='Détail', track_visibility='onchange')
    confirm_service_commercial = fields.Boolean(string='Confirmation Service Commercial', default=False, track_visibility='onchange')
    delivery_noconform_treated = fields.Boolean(string='Livraison non conforme traitée', default=False, track_visibility='onchange')
    confirm_accounting = fields.Boolean(string='Confirmation Comptabilité', default=False, track_visibility='onchange')
    bl_conform = fields.Boolean(string='BL Conforme', default=False, track_visibility='onchange')
    bl_emarge = fields.Boolean(string='BL Emargé', default=False, track_visibility='onchange')  
    
    def _compute_weight_total_stock_agn(self):
        for sales in self:
            weight_stock_agn = 0
            for line in sales.order_line:
                if "AGNEAU FRAIS" in line.product_id.categ_id.complete_name or "AGNEAU" in line.product_id.categ_id.complete_name:
                    weight_stock_agn += line.product_uom_qty  or 0.0
            sales.total_weight_stock_agn = weight_stock_agn
            
    def _compute_weight_total_stock_epc(self):
        for sales in self:
            weight_stock_epc = 0
            for line in sales.order_line:
                if "Aides cuisines" in line.product_id.categ_id.complete_name or "BOISSONS" in line.product_id.categ_id.complete_name or "Patés" in line.product_id.categ_id.complete_name or "BOUILLONS" in line.product_id.categ_id.complete_name or "CONSERVES" in line.product_id.categ_id.complete_name or "FRUITS SECS" in line.product_id.categ_id.complete_name or "FÉCULANTS" in line.product_id.categ_id.complete_name or "HUILE" in line.product_id.categ_id.complete_name or "Soupe" in line.product_id.categ_id.complete_name or "INFUSIONS" in line.product_id.categ_id.complete_name or "Légumes secs" in line.product_id.categ_id.complete_name or "Produits frais" in line.product_id.categ_id.complete_name or "Riz" in line.product_id.categ_id.complete_name or "SALADES" in line.product_id.categ_id.complete_name or  "SALÉES" in line.product_id.categ_id.complete_name or "SUCRES" in line.product_id.categ_id.complete_name or "Sauces" in line.product_id.categ_id.complete_name or "Sauces Promo" in line.product_id.categ_id.complete_name or "THÉ" in line.product_id.categ_id.complete_name or "VINAIGRE" in line.product_id.categ_id.complete_name or "Épices" in line.product_id.categ_id.complete_name or "Pot de bébé" in line.product_id.categ_id.complete_name:
                    weight_stock_epc += line.product_uom_qty  or 0.0
            sales.total_weight_stock_epc = weight_stock_epc
            
            
    @api.model
    def fields_get(self, fields=None):
        fields_to_hide = ['user_id']
        res = super(SaleOrder, self).fields_get()
        for field in fields_to_hide:
            res[field]['selectable'] = False
        return res
    
    @api.onchange('cmd_charcuterie', 'cmd_volaille')
    def onchange_payment_term_id_so(self):
        for sale in self:
            if sale.cmd_charcuterie:
                payment_term = self.env['account.payment.term'].search([('name', '=', 'CHARCUTERIE ÉCHÉANCE')])
                sale.payment_term_id = payment_term
            if sale.cmd_volaille:
                payment_term = self.env['account.payment.term'].search([('name', '=', 'VOLAILLES ÉCHÉANCE')])
                sale.payment_term_id = payment_term
            if (sale.cmd_charcuterie and sale.cmd_volaille) or (not sale.cmd_charcuterie and not sale.cmd_volaille):
                sale.payment_term_id = False
                
                
    @api.onchange('cmd_volaille','cmd_charcuterie')
    def onchange_type_of_commande(self):
        for sale in self:
            if sale.cmd_volaille:
                sale.commande_type = 'commande_volaille'
            else:
                sale.commande_type = 'commande_charc'
                
                
    @api.onchange('partner_id')
    def _get_type_cmd(self):
        for sale in self:
            if sale.partner_id.Client_Charcuterie:
                sale.cmd_charcuterie = True
            if sale.partner_id.Client_Volaille:
                sale.cmd_volaille = True
            if sale.partner_id.debloque_exce_ch:
                sale.debloque_exce_vopp = True
    
    @api.multi
    def compute_qty_transport(self):
        for line in self:
            object = self.env['sale.order.line']
            product = self.env['product.template'].search([('name', '=', 'TRANSPORT GRAND COMPTE')])
            productorigine = self.env['product.product'].search([('product_tmpl_id', '=', product.id)])
            dict = 0
            p = self.env['sale.order.line'].search([('product_id', '=', productorigine.id),('order_id','=',line.id)])
            if len(p) == 0:
                for lines in line.order_line:
                    if lines.product_id:
                        dict += lines.secondary_uom_qty
                object_create = object.create({
                'product_id': productorigine.id,
                'product_uom_qty': 1,
                'secondary_uom_qty': 1,
                'qty_delivered':1,
                'product_uom': product.uom_id.id,
                'order_id':line.id,
                'name':product.name,
                'price_unit':product.list_price,
                'volume_tot':productorigine.list_price
                })
            else:
                dict = 0
                product_already_exist = self.env['sale.order.line'].search([('product_id', '=', productorigine.id),('order_id','=',line.id)])
                for lines in line.order_line:
                    if lines.product_id and (lines.product_id.name != 'TRANSPORT GRAND COMPTE'):
                        dict += lines.secondary_uom_qty
                object_create = product_already_exist.write({
                'product_id': productorigine.id,
                'product_uom_qty': 1,
                'secondary_uom_qty': 1,
                'qty_delivered':1,
                'product_uom': product.uom_id.id,
                'order_id':line.id,
                'name': product.name,
                'price_unit':product.list_price,
                'volume_tot':productorigine.list_price
                })
    
    
    def _compute_colis_total_ordred(self):
        for sale in self:
            total_qty_ordred1 = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_ordred1 += line.product_uom_qty or 0.0
            sale.total_qty_ordred1 = total_qty_ordred1

    def _compute_colis_total_delivred(self):
        for sale in self:
            total_qty_delivred = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_delivred += line.qty_delivered or 0.0
            sale.total_qty_delivred = total_qty_delivred

    def _compute_colis_total_invoiced(self):
        for sale in self:
            total_qty_invoiced = 0
            for line in sale.order_line:
                if line.product_id:
                    total_qty_invoiced += line.qty_invoiced or 0.0
            sale.total_qty_invoiced = total_qty_invoiced

    def _compute_colis_total_etat(self):
        for sale in self:
            if sale.total_qty_invoiced == 0:
                sale.etat_fac1 = "A facturer"
            if sale.total_qty_invoiced > 0 :
                sale.etat_fac1 = "facturé"
                
    @api.depends('order_line.qty_invoiced','state','refused_command')                
    def _compute_colis_total_etat_copy(self):
        for sale in self:
            if sale.total_qty_invoiced == 0:
                sale.etat_fac1_copy = "A facturer"
            if sale.total_qty_invoiced > 0 :
                sale.etat_fac1_copy = "Facturée"
            if sale.state == "cancel":
                sale.etat_fac1_copy = "Annulée"
            if sale.refused_command:
                sale.etat_fac1_copy = "A ne pas facturer"
                

#@api.onchange('partner_id')
# def on_change_statecr(self):
#    for record in self:
#     if record.partner_id.bloque:
#        record.test_bloque="bloquer"
#        raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement !'))
#        return {'warning': {'title': _('Error'), 'message': _('Error message'),},}

                

    @api.onchange('partner_id','cmd_charcuterie','cmd_volaille')
    def on_change_statecr(self):
        for record in self:
            if record.partner_id:
                if record.cmd_charcuterie==True:
                    if record.partner_id.Client_Charcuterie==False:
                        raise exceptions.ValidationError(_('Votre Client ne peux pas passer une commande charcuterie veuillez modifier le type de votre client sur sa fiche ! ')) 
                        return {
                            'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
                if record.cmd_volaille==True:
                    if record.partner_id.Client_Volaille==False:
                        raise exceptions.ValidationError(_('Votre Client ne peux pas passer une commande volaille veuillez modifier le type de votre client sur sa fiche ! ')) 
                        return {
                            'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
                if record.partner_id.bloque_ch:
                    record.test_bloque="Votre Client est bloqué"
                if record.partner_id.bloque_vo:
                    record.test_bloque="Votre Client est bloqué"
                if record.partner_id.bloque_ch and record.partner_id.bloque_vo:
                    record.test_bloque="Votre Client est bloqué"
                
                
                
                
            '''if record.cmd_charcuterie==True and record.cmd_volaille==False:
                if record.partner_id.Client_Charcuterie: 
                    if record.partner_id.credit_charcuterie > record.partner_id.limite_credit_charcuterie: 
                        if record.partner_id.bloque_ch  and record.partner_id.debloque_exce_ch==False:
                            record.test_bloque="bloquer"
                            raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement de vos factures charcuteries!'))
                            return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
                        
            if record.cmd_charcuterie==True and record.cmd_volaille==False:
                if record.partner_id.Client_Charcuterie: 
                    if record.partner_id.credit_charcuterie > record.partner_id.limite_credit_charcuterie: 
                        if record.partner_id.bloque_ch and record.partner_id.debloque_exce_ch==True:
                            record.test_bloque=""

            if record.cmd_charcuterie==True and record.cmd_volaille==False:
                if record.partner_id.Client_Charcuterie: 
                    if record.partner_id.nbr_jours_decheance_charcuterie > record.partner_id.echeance_charcuterie_par_jour: 
                        if record.partner_id.bloque_ch and record.partner_id.debloque_exce_ch==False:
                            record.test_bloque="bloquer"
                            raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement de vos factures charcuteries!'))
                            return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
            if record.cmd_charcuterie==True and record.cmd_volaille==False:
                if record.partner_id.Client_Charcuterie: 
                    if record.partner_id.nbr_jours_decheance_charcuterie > record.partner_id.echeance_charcuterie_par_jour: 
                        if record.partner_id.bloque_ch and record.partner_id.debloque_exce_ch==True:
                            record.test_bloque=""                      
                        
                        
            if record.cmd_charcuterie==False and record.cmd_volaille==True: 
                if record.partner_id.Client_Volaille: 
                    if record.partner_id.credit_volaille > record.partner_id.credit_limit: 
                        if record.partner_id.bloque_vo and record.partner_id.debloque_exce_vo==False:
                            record.test_bloque="bloquer"
                            raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement de vos factures volailles!'))
                            return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
            if record.cmd_charcuterie==False and record.cmd_volaille==True: 
                if record.partner_id.Client_Volaille: 
                    if record.partner_id.credit_volaille > record.partner_id.credit_limit: 
                        if record.partner_id.bloque_vo and record.partner_id.debloque_exce_vo==True:
                            record.test_bloque=""
                            
            if record.cmd_charcuterie==False and record.cmd_volaille==True:
                if record.partner_id.Client_Volaille: 
                    if record.partner_id.nbr_fac_ouverte >= record.partner_id.limite_nbr_fac: 
                        if record.partner_id.bloque_vo and record.partner_id.debloque_exce_vo==False:
                            record.test_bloque="bloquer"
                            raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement de vos factures volailles!'))
                            return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
            if record.cmd_charcuterie==False and record.cmd_volaille==True:
                if record.partner_id.Client_Volaille: 
                    if record.partner_id.nbr_fac_ouverte >= record.partner_id.limite_nbr_fac: 
                        if record.partner_id.bloque_vo and record.partner_id.debloque_exce_vo==True:
                            record.test_bloque=""'''
                
    @api.onchange('order_line','test_bloque')                
    def _compute_bloque_ch(self):
        for sale in self:
            if sale.partner_id:
                if sale.partner_id.blocagex_echeance_facture_charcuterie==True:                
                    if sale.partner_id.nbr_jours_decheance_charcuterie > sale.partner_id.echeance_charcuterie_par_jour:
                        partner_id=self.env['res.partner'].search([('id', '=', sale.partner_id.id)],limit=1)
                        partner_id.write({'bloque_ch': True,'bloque': True})
                
                
    

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
            #'qty_livrer_colis': self.env['stock.picking'].search([('state', '=', 'done'),('picking_type_id.code', '=', 'outgoing'),('origin', '=', self.name)],limit=1).total_colis_delivered - self.picking_ids.filtered(lambda r: r.picking_type_id.code == 'incoming' and r.state == 'done').total_colis_delivered ,
            'commercial': self.user_id.id,
            'vendeur': self.vendeur.id,
            'account_id': self.partner_invoice_id.property_account_receivable_id.id,
            'partner_id': self.partner_invoice_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'journal_id': journal_id,
            'ref_livraison':self.env['stock.picking'].search([('state', '=', 'done'),('picking_type_id.code', '=', 'outgoing'),('origin', '=', self.name)],limit=1).id,
            'date_commande': self.date_order,
            'date_livraison': self.requested_date,
            'currency_id': self.pricelist_id.currency_id.id,
            'comment': self.note,
            'payment_term_id': self.payment_term_id.id,
            'fiscal_position_id': self.fiscal_position_id.id or self.partner_invoice_id.property_account_position_id.id,
            'company_id': self.company_id.id,
            'user_id': self.env.user.id,
            'team_id': self.team_id.id,
            
        }
        return invoice_vals
    
    @api.multi
    def action_confirm(self):
        products = self.order_line.mapped('product_id')
        for product in products:
            cmpt = 0
            for order in self.order_line:
                if order.product_id.id == product.id:
                    cmpt+= 1
            if cmpt>1:
                raise UserError(_(
                'Article en double: %s'
                ) % (product.name))
        if (self.cmd_charcuterie and self.cmd_volaille) or (not self.cmd_charcuterie and not self.cmd_volaille):
            raise exceptions.ValidationError(_('Merci de specifier le type de la commande !'))
            return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
        
        if not self.vendeur  or not self.user_id:
            raise exceptions.ValidationError(_('Merci de mentionner vendeur/commercial !'))
            return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
            
        if self.cmd_charcuterie==True and self.debloque_exce_vopp==False and self.cmd_volaille==False:
            if self.partner_id.Client_Charcuterie: 
                if self.partner_id.credit_charcuterie > self.partner_id.limite_credit_charcuterie: 
                    if self.partner_id.bloque_ch:
                        if self.partner_id.debloque_exce_ch==False:
                            self.test_bloque="bloquer"
                            raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement de vos factures charcuteries!'))
                            return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
                        if self.partner_id.debloque_exce_ch==True:
                            self.test_bloque=""
        if self.cmd_charcuterie==True and self.debloque_exce_vopp==False and self.cmd_volaille==False:
            if self.partner_id.Client_Charcuterie: 
                if self.partner_id.nbr_jours_decheance_charcuterie > self.partner_id.echeance_charcuterie_par_jour: 
                    if self.partner_id.bloque_ch:
                        if self.partner_id.debloque_exce_ch==False:
                            self.test_bloque="bloquer"
                            raise exceptions.ValidationError(_('Votre Client est bloqué , merci de  procéder au réglement de vos factures charcuteries!'))
                            return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                            }
                        if self.partner_id.debloque_exce_ch==True:
                            self.test_bloque=""
        if self.cmd_charcuterie==False  and self.debloque_exce_vopp==False and self.cmd_volaille==True: 
            if self.partner_id.Client_Volaille: 
                if self.partner_id.credit_volaille > self.partner_id.credit_limit: 
                    if self.partner_id.bloque_vo==True:
                        self.test_bloque="bloquer"
                        raise exceptions.ValidationError(_('Votre Client est bloqué , son credit et depassé, merci de  procéder au réglement de vos factures volailles!'))
                        return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }

                            
        if self.cmd_charcuterie==False and self.cmd_volaille==True and self.debloque_exce_vopp==False:
            if self.partner_id.Client_Volaille: 
                if self.partner_id.nbr_fac_ouverte >= self.partner_id.limite_nbr_fac: 
                    if self.partner_id.bloque_vo==True:
                        self.test_bloque=="bloquer"
                           # record.cmd_excep=self.env['res.partner'].search([('id', '=', sales.partner_id.id)]).bloque_vo
                        raise exceptions.ValidationError(_('Votre Client est bloqué , nombre de factures ouvertes depasse les limites, merci de  procéder au réglement de vos factures volailles!'))
                        return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }
        if self.partner_id.blocagex_echeance_facture_charcuterie==True:                
            if self.partner_id.nbr_jours_decheance_charcuterie > self.partner_id.echeance_charcuterie_par_jour:
                           # record.cmd_excep=self.env['res.partner'].search([('id', '=', sales.partner_id.id)]).bloque_vo
                raise exceptions.ValidationError(_('Votre Client est bloqué ,  merci de  procéder au réglement!'))
                return {
                                'warning': {'title': _('Error'), 'message': _('Error message'),},
                }
            
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))
        self._action_confirm()
        if self.env['ir.config_parameter'].sudo().get_param('sale.auto_done_setting'):
            self.action_done()
        return True

    def _compute_weight_total(self):
        for sale in self:
            weight_tot = 0
            for line in sale.order_line:
                if line.product_id:
                    weight_tot += line.weight or 0.0
            sale.total_weight = weight_tot

    def _compute_colis_total(self):
        for sale in self:
            total_colis = 0
            for line in sale.order_line:
                if line.product_id and line.product_id.type != 'service':
                    total_colis += line.secondary_uom_qty or 0.0
            sale.total_colis = total_colis
            
    #compute total colis delivered       
    def _compute_colis_livrer_total(self):
        for sale in self:
            total_colis = 0
            for line in sale.order_line:
                print('sale order')
                if line.product_id and line.product_id.type != 'service' and line.secondary_uom_id:
                    if line.product_uom_qty-line.qty_delivered <= ((-1)* line.secondary_uom_id.factor) and line.product_id.uom_id.name =='kg':
                        total_colis += int(line.product_uom_qty) + int((line.qty_delivered-line.product_uom_qty)/line.secondary_uom_id.factor) or 0.0
                    if line.product_uom_qty-line.qty_delivered > ((-1)* line.secondary_uom_id.factor) and line.product_id.uom_id.name =='kg' and line.qty_delivered !=0 and float_compare(line.product_uom_qty, line.qty_delivered, precision_rounding=line.product_uom.rounding)< 0:
                        total_colis += line.secondary_uom_qty
                    if line.product_uom_qty-line.qty_delivered >= (line.secondary_uom_id.factor) and line.product_id.uom_id.name =='kg':
                        total_colis += int(line.product_uom_qty) - int((line.product_uom_qty-line.qty_delivered)/line.secondary_uom_id.factor) or 0.0
                    if line.product_uom_qty-line.qty_delivered < (line.secondary_uom_id.factor) and line.product_id.uom_id.name =='kg' and line.qty_delivered !=0 and line.qty_delivered !=0 and float_compare(line.product_uom_qty, line.qty_delivered, precision_rounding=line.product_uom.rounding)> 0:
                        total_colis += line.secondary_uom_qty
                    if line.product_id.uom_id.name !='kg':
                        total_colis += line.qty_delivered or 0.0
            sale.total_colis_livrer = total_colis
            

    def _compute_volumeht_total(self):
        for sale in self:
            total_volum_ht = 0
            for line in sale.order_line:
                if line.product_id:
                    total_volum_ht += (line.volume_tot * (line.tax_id.amount/100))+line.volume_tot or 0.0
            sale.total_volume_ht = total_volum_ht

    def _compute_ht_total(self):
        for sale in self:
            total_ht = 0
            for line in sale.order_line:
                if line.product_id:
                    total_ht += line.volume_tot or 0.0
            sale.total_ht = total_ht
            

    '''@api.onchange('partner_id')
    def onchange_get_default_ven(self):
        for sale in self:
            if sale.partner_id :
                partner_id = sale.partner_id.id
                sale.vendeur = sale.partner_id.vendeur
                sale.user_id = sale.partner_id.user_id
            # partners.user_id=vendeur_commarcial'''
            
    @api.depends('partner_id')
    @api.onchange('partner_id')
    def onchange_get_default_ven(self):
        for sale in self:
            if sale.partner_id :
                partner_id = sale.partner_id.id
                sale.vendeur = sale.partner_id.vendeur
                sale.user_id = sale.partner_id.user_id
            # partners.user_id=vendeur_commarcial
            
    @api.multi    
    @api.onchange('partner_id')
    def get_default(self):
        for sales in self:
            Bolocagettm = 0
            if sales.partner_id :
                productbl = self.env['res.partner'].search([
                ('id', '=', sales.partner_id.id)])
                Bolocagettm = productbl.Bolocagettm.id
            sales.Bolocagettm = Bolocagettm
            sales.Bolocagettm_id = Bolocagettm
            
            
    @api.one    
    @api.depends('partner_shipping_id')
    def get_default_zip(self):
        for sales in self:
            zip_df = ""
            adresse_liv = ""
            city = ""
            if sales.partner_shipping_id :
                productblzip = self.env['res.partner'].search([
                ('id', '=', sales.partner_shipping_id.id)])
                zip_df = productblzip.zip
                adresse_liv = productblzip.street
                city = productblzip.city
            sales.zip_df=zip_df
            sales.adresse_liv=adresse_liv
            sales.city=city                        
            
    def _compute_weight_total_stock_char(self):
        for sales in self:
            weight_stock_char = 0
            for line in sales.order_line:
#                if line.product_id.categ_id.complete_name in ("Chips","Saucissons","Chapelet","Mortadelle","Blocs","Panes","Tranches","Charcuterie Promo"):
                if "Chips" in line.product_id.categ_id.complete_name or "Saucissons" in line.product_id.categ_id.complete_name or "Chapelet" in line.product_id.categ_id.complete_name or "Mortadelle" in line.product_id.categ_id.complete_name or "Blocs" in line.product_id.categ_id.complete_name or "Panes Charcuterie" in line.product_id.categ_id.complete_name or "Tranches" in line.product_id.categ_id.complete_name or "Tranches Promo" in line.product_id.categ_id.complete_name or "Saucissons Promo" in line.product_id.categ_id.complete_name or "Panes Charcuterie Promo" in line.product_id.categ_id.complete_name:
                    weight_stock_char += line.secondary_uom_qty  or 0.0
            sales.total_weight_stock_char = weight_stock_char
            
    def _compute_weight_total_stock_srg(self):
        for sales in self:
            weight_stock_srg = 0
            for line in sales.order_line:
                if "Surgeles" in line.product_id.categ_id.complete_name or "Galette Surgele" in line.product_id.categ_id.complete_name or "IQF" in line.product_id.categ_id.complete_name or "Surgelé Non Carné" in line.product_id.categ_id.complete_name or "Galette Surgele" in line.product_id.categ_id.complete_name:
                    weight_stock_srg += line.secondary_uom_qty  or 0.0
            sales.total_weight_stock_srg = weight_stock_srg
            
    def _compute_weight_total_stock_vv(self):
        for sales in self:
            weight_stock_vv = 0
            for line in sales.order_line:
                if "V-Nouvelle atlas" in line.product_id.categ_id.complete_name or "UVESA" in line.product_id.categ_id.complete_name or "DAJAJ" in line.product_id.categ_id.complete_name or "Volaille Frais" in line.product_id.categ_id.complete_name or "Panes VV" in line.product_id.categ_id.complete_name or "Panes Volaille" in line.product_id.categ_id.complete_name or "Panes Volaille Promo" in line.product_id.categ_id.complete_name or "Volaille Promo" in line.product_id.categ_id.complete_name or "Produit élaboré" in line.product_id.categ_id.complete_name:
                    weight_stock_vv += line.product_uom_qty  or 0.0
            sales.total_weight_stock_vv = weight_stock_vv
    
    @api.onchange('order_line','order_line.product_id','order_line.product_uom_qty')
    def onchange_order_line_livre(self):
        for record in self:
            record._compute_weight_total_stock_vv()
            record._compute_weight_total_stock_srg()
            record._compute_weight_total_stock_char()
            record.get_product_ttm()
                    
    @api.depends('total_weight_stock_char','total_weight_stock_srg','total_weight_stock_vv')
    def get_product_ttm(self):
        for sales in self:
            if  sales.total_weight_stock_vv == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_char != 0 and sales.total_weight_stock_srg != 0:
                sales.produitalivrer="Charc + Surg"
            if  sales.total_weight_stock_vv == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_char == 0 and sales.total_weight_stock_srg != 0:
                sales.produitalivrer=" Surg"
            if sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_char != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="Charc + VV"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_char == 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer=" VV"
            if sales.total_weight_stock_char == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_srg != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="VV + Surg"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0:
                sales.produitalivrer=" Charc"
            if sales.total_weight_stock_char != 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_srg != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="Charc + Surg + VV"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="AGN"
            if  sales.total_weight_stock_srg != 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="Surg + AGN"
            if  sales.total_weight_stock_srg != 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_vv != 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="Surg + AGN + VV"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_vv != 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="AGN + VV"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc == 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0:
                sales.produitalivrer="AGN + Charc"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="EPC"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="EPC+ AGN"
            if  sales.total_weight_stock_srg != 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="Surg + EPC+ AGN"
            if  sales.total_weight_stock_srg != 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv != 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="Surg + EPC+ AGN + VV"
            if  sales.total_weight_stock_srg != 0 and sales.total_weight_stock_agn != 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0:
                sales.produitalivrer="Surg + EPC+ AGN + Charc"
            if  sales.total_weight_stock_srg != 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0:
                sales.produitalivrer="Surg + EPC + Charc"
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0:
                sales.produitalivrer="EPC + Charc"
            if  sales.total_weight_stock_srg != 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="EPC + Surg "
            if  sales.total_weight_stock_srg == 0 and sales.total_weight_stock_agn == 0 and sales.total_weight_stock_epc != 0 and sales.total_weight_stock_vv != 0 and sales.total_weight_stock_char == 0:
                sales.produitalivrer="EPC + VV "
                
    @api.model
    def create(self, vals):
        sale = super(SaleOrder,self).create(vals)
        '''if any(line.secondary_uom_qty == 0.0 for line in sale.order_line):
            raise exceptions.ValidationError(_('Remplir les QTY !'))
            return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }  '''
        if sale.cmd_volaille:
                sale.commande_type = 'commande_volaille'
        else:
            sale.commande_type = 'commande_charc'  
        
        if ('cmd_charcuterie' in vals and vals['cmd_charcuterie'] and 'cmd_volaille' in vals and vals['cmd_volaille']) or ('cmd_charcuterie' in vals and not vals['cmd_charcuterie'] and 'cmd_volaille' in vals and not vals['cmd_volaille']):
            raise exceptions.ValidationError(_('Merci de specifier le type de la commande !'))
            return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
        
        return sale
    
    @api.multi
    def write(self, vals):
        sale = super(SaleOrder,self).write(vals)
        '''if any(line.secondary_uom_qty == 0.0 for line in self.order_line):
            raise exceptions.ValidationError(_('Remplir les QTY !'))
            return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }  '''
        if (self.cmd_charcuterie and self.cmd_volaille) or (not self.cmd_charcuterie and not self.cmd_volaille):
            raise exceptions.ValidationError(_('Merci de specifier le type de la commande !'))
            return {
                    'warning': {'title': _('Error'), 'message': _('Error message'),},
            }
             
        return sale