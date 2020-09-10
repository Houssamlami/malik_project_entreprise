# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import Controller, request


class FCustomerPortal(CustomerPortal):
    
    
    def _prepare_portal_layout_values(self):
        #res = super(FCustomerPortal, self)._prepare_portal_layout_values()
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id.user_id._is_public():
            sales_user = partner.user_id.user_id
            
        return {
            'sales_user': sales_user,
            'page_name': 'home',
            'archive_groups': [],
            }
        
        #return res