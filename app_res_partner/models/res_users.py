# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, exceptions, _



class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def create(self, vals):
        user = super(ResUsers, self).create(vals)
        user.partner_id.customer = False
        return user