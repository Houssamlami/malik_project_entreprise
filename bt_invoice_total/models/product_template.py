# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
import string

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    facture_kg = fields.Boolean(string='Facturation en KG')
    