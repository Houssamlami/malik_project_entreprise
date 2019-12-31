# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoiceDraftWizard(models.TransientModel):
    _name = "sol.update.qty.wizard"
    _description = "SOL update qty"

    @api.multi
    def update_sols(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        sol = self.env['sale.order.line'].browse(active_ids)
        for sols in sol:
            sols.get_default_fact_qty()
