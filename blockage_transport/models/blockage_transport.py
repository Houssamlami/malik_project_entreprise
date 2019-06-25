# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api

class BlockageBlockage(models.Model):

    _name = "blockage.blockage"
    
    name = fields.Char(string='Name')



class ResPartner(models.Model):
    _inherit = "res.partner"

    Bolocagettm = fields.Many2one('blockage.blockage')

	
class SaleOrder(models.Model):


    _inherit = "sale.order"

    Bolocagettm = fields.Integer('blo')
    Bolocagettm_id = fields.Many2one(comodel_name='blockage.blockage')
    total_weight_stock_char = fields.Float(string='Total charcuterie)', compute='_compute_weight_total_stock_char')
    total_weight_stock_srg = fields.Float(string='Total surgele)', compute='_compute_weight_total_stock_srg')
    total_weight_stock_vv = fields.Float(string='Total volaille)', compute='_compute_weight_total_stock_vv')
    produitalivrer = fields.Char('Produit a livrer', compute='get_product_ttm', store=True)
    Expediteur =  fields.Selection([('MV', 'Malik V'), ('An', 'Atlas N')])	
    zip_df =  fields.Char(string='CP', compute='get_default_zip')
    adresse_liv =  fields.Char(string='Adresse livraison', compute='get_default_zip')
    city =  fields.Char(string='Ville', compute='get_default_zip')	
    observation =  fields.Char(string='Observation')
	
	

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
    @api.depends('partner_id')
    def get_default_zip(self):
        for sales in self:
            zip_df = ""
            adresse_liv = ""
            city = ""
            if sales.partner_id :
                productblzip = self.env['res.partner'].search([
                ('id', '=', sales.partner_id.id)])
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
                if line.product_id.categ_id.parent_id.name in ("Sauces","Chips","Saucissons","Chapelet","Mortadelle","Blocs","Panes","Tranches"):
                    weight_stock_char += line.product_uom_qty  or 0.0
            sales.total_weight_stock_char = weight_stock_char
			
    def _compute_weight_total_stock_srg(self):
        for sales in self:
            weight_stock_srg = 0
            for line in sales.order_line:
                if line.product_id.categ_id.parent_id.name in ("Surgeles","IQF"):
                    weight_stock_srg += line.product_uom_qty  or 0.0
            sales.total_weight_stock_srg = weight_stock_srg
			
    def _compute_weight_total_stock_vv(self):
        for sales in self:
            weight_stock_vv = 0
            for line in sales.order_line:
                if line.product_id.categ_id.parent_id.name in ("Volaille","Volailles Espagne","La Volailles BON","Volailles IMEX"):
                    weight_stock_vv += line.product_uom_qty  or 0.0
            sales.total_weight_stock_vv = weight_stock_vv
			
			
	
    @api.depends('total_weight_stock_char','total_weight_stock_srg','total_weight_stock_vv')
    def get_product_ttm(self):
        for sales in self:
            if  sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0 and sales.total_weight_stock_srg != 0:
                sales.produitalivrer="Charc + Surg"
            if  sales.total_weight_stock_vv == sales.total_weight_stock_char == 0 and sales.total_weight_stock_srg != 0:
                sales.produitalivrer=" Surg"
            if sales.total_weight_stock_srg == 0 and sales.total_weight_stock_char != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="Charc + VV"
            if  sales.total_weight_stock_srg == sales.total_weight_stock_char == 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer=" VV"
            if sales.total_weight_stock_char == 0 and sales.total_weight_stock_srg != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="VV + Surg"
            if  sales.total_weight_stock_srg == sales.total_weight_stock_vv == 0 and sales.total_weight_stock_char != 0:
                sales.produitalivrer=" Charc"
            if sales.total_weight_stock_char != 0 and sales.total_weight_stock_srg != 0 and sales.total_weight_stock_vv != 0:
                sales.produitalivrer="Charc + Surg + VV"
# class SaleOrder(models.Model):
    # _inherit = "sale.order"
	
    # blocake= fields.Many2one('head.branch', string='Head/Branch', index=True, ondelete='cascade', default=_default_head_branch)
	
    # def _default_head_branch(self):

        # return self.env['res.partner'].search([('partner_id', '=', self.partner_id)], limit=1).blocake
    # @api.depends('partner_id')	
    # def _select_blocage(self):
        # for sales in self:
            # blocake = ''
            # if sales.partner_id:
                # blocake += sales.partner_id.Bolocagettm
            # sales.blocake = blocake
	
	
