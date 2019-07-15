# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _



class Marchandises(models.Model):
    
    _name = "marchandises.client"
    
    name = fields.Char(string='Marchandise',required=True)
