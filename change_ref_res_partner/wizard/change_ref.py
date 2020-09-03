# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models



class ResPartnerRefWizard(models.TransientModel):
    _name = "res.partner.ref.wizard"
    

    @api.multi
    def change_ref_partner_res(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        partners = self.env['account.invoice'].browse(active_ids)
        partners = partners.filtered(lambda o: o.state in ['draft'])
        for partner in partners:
            partner.ref = ''
