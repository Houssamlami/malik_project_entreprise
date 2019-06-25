# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import except_orm, Warning, RedirectWarning
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
    
    
class ProductTemplate(models.Model):

    _inherit = 'product.template'
    
    
''' @api.multi
    def _check_security_action7(self):
        if self.env.user.has_group('restriction_pricelist_priceunit.group_to_write_create_unlink_product'):
            raise UserError(_('Vous avez pas le droit de créer un produit'))
    
    @api.multi
    def _check_security_action8(self):
        if self.env.user.has_group('restriction_pricelist_priceunit.group_to_write_create_unlink_product'):
            raise UserError(_('Vous avez pas le droit de modifier un produit'))
        
    @api.multi
    def _check_security_action9(self):
        if self.env.user.has_group('restriction_pricelist_priceunit.group_to_write_create_unlink_product'):
            raise UserError(_('Vous avez pas le droit de suprimmer un produit'))
   
    @api.model
    def create(self, vals):
        product = super(ProductTemplate, self).create(vals)
        self._check_security_action7()
        
        return product
        
    
    @api.multi
    def write(self, vals):
        product = super(ProductTemplate, self).write(vals)
        self._check_security_action8()
        return product
    
    @api.multi
    def unlink(self):
        product = super(ProductTemplate, self).unlink()
        self._check_security_action8()
        return product
        
'''