# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.stock_barcode.controllers.main import StockBarcodeController

class StockBarcodeController(StockBarcodeController):

    def try_open_picking(self, barcode):
        """ If barcode represents a picking, open it
        """
        corresponding_picking = request.env['stock.picking'].search([
            ('name', '=', barcode),
            ('state', 'in', ('partially_available', 'assigned','done'))
        ], limit=1)
        if corresponding_picking:
            action_picking_form = request.env.ref('stock_barcode.stock_picking_action_form')
            action_picking_form = action_picking_form.read()[0]
            action_picking_form['res_id'] = corresponding_picking.id
            return {'action': action_picking_form}
        return False

