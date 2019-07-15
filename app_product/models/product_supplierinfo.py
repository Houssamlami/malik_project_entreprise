# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _




class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"
    
    
    nbr_km = fields.Integer(string='KM')