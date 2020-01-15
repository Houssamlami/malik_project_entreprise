# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models



class AccountInvoiceCancelWizard(models.TransientModel):
    _name = "account.invoice.change.move.name"
    _description = "Wizard - Account Invoice Validate"

    @api.multi
    def change_move_name_invoices(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        invoices = self.env['account.invoice'].browse(active_ids)
        invoices = invoices.filtered(lambda o: o.state in ['draft'])
        for invoice in invoices:
            invoice.move_name = ''
