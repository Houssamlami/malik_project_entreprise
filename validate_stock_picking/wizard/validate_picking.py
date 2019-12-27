# -*- coding: utf-8 -*-
# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrderConfirmWizard(models.TransientModel):
    _name = "stock.picking.confirm.wizard"
    _description = "Wizard - Stock picking Confirm"

    @api.multi
    def confirm_stock_pickings(self):
        self.ensure_one()
        active_ids = self.env.context.get('active_ids')
        pickings = self.env['stock.picking'].browse(active_ids)
        pickings = pickings.filtered(lambda o: o.state not in ['cancel', 'done'])
        for picking in pickings:
            picking.button_validate()
