# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
from odoo.exceptions import Warning


class StockPicking(models.Model):
    _inherit = "stock.picking"

    barcode_scan1 = fields.Char(string="Scan Barcode Here")

    @api.onchange('barcode_scan1')
    def barcode_scan(self):
        if self.picking_type_id:
            if self.barcode_scan1:
                print("\n\n\n self-->", self.id)
                is_product = True
                is_lot = True
                today = datetime.today()
                today_year = str(today.year)
                barcode = self.barcode_scan1
                reference = barcode[4:18]
                if reference:
                    product_id = self.env['product.product'].search([('default_code', '=', reference)], limit=1)
                    if not product_id:
                        is_product = False
                else:
                    raise Warning(_('Please Scan Properly'))

                lot_number = barcode[42:]
                print("\n\n\n lot_number", lot_number)
                if lot_number:
                    lot_id = self.env['stock.production.lot'].search([('name', '=', lot_number)], limit=1)
                    if not lot_id:
                        is_lot = False
                else:
                    raise Warning(_('Please Scan Properly'))

                date1 = barcode[32:38]
                year = date1[0:2]
                month = date1[2:4]
                day = date1[4:]
                if date1:
                    manufacturing_date = date(year=int(today_year[0:2] + str(year)), month=int(month), day=int(day))
                    if manufacturing_date:
                        raise Warning(_('Manufacturing Date not Found!!!'))
                else:
                    raise Warning(_('Please Scan Properly'))

                if is_product and is_lot:
                    dict1 = {
                        'product_id': product_id.id,
                        'lot_id': lot_id.id,
                        'manufacturing_date': manufacturing_date,
                    }
                    dict2 = {
                        'product_id': product_id.id,
                        'manufacturing_date': manufacturing_date,
                        'product_uom': product_id.uom_id.id
                    }
                    self.move_line_ids_without_package = [(0, 0, dict1)]
                    self.move_ids_without_package = [(0, 0, dict2)]
                    self.barcode_scan1 = ''
                elif not is_product and is_lot:
                    dict1 = {
                        'product_id': lot_id.product_id.id,
                        'lot_id': lot_id.id,
                        'manufacturing_date': manufacturing_date,
                    }
                    dict2 = {
                        'product_id': lot_id.product_id.id,
                        'manufacturing_date': manufacturing_date,
                        'product_uom': lot_id.product_id.uom_id.id
                    }
                    self.move_line_ids_without_package = [(0, 0, dict1)]
                    self.move_ids_without_package = [(0, 0, dict2)]
                    self.barcode_scan1 = ''
                elif not is_lot and is_product:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Wizard',
                        'view_mode': 'form',
                        'res_model': 'wizard.details',
                        # 'res_id': self.env.company.id,
                        'target': 'new',
                        'context': {
                            'default_is_lot': False,
                            'default_is_product': True,
                            'default_name': product_id.name,
                        },
                    }
                elif not is_lot and not is_product:
                    return {
                        'type': 'ir.actions.act_window',
                        'name': 'Wizard',
                        'view_mode': 'form',
                        'res_model': 'wizard.details',
                        'res_id': False,
                        'target': 'new',
                        'context': {
                            'default_is_lot': False,
                            'default_is_product': False,
                        },
                    }


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    manufacturing_date = fields.Date(string="Manufacturing Date")


class StockMove(models.Model):
    _inherit = "stock.move"

    manufacturing_date = fields.Date(string="Manufacturing Date")

    @api.model
    def create(self, vals):
        return super(StockMove, self).create(vals)


class WizardDetails(models.TransientModel):
    _name = "wizard.details"

    name = fields.Char(string="Product Name")
    lot_name = fields.Char(string="Lot Number")
    reference = fields.Char()
    is_lot = fields.Boolean(default=False)
    is_product = fields.Boolean(default=False)

    def action_save_product_and_lot(self):
        if self.lot_name and self.name and not self.reference:
            id = self.env['product.product'].search([('name', '=', self.name)], limit=1)
            lot_id = self.env['stock.production.lot'].create({'name': self.lot_name, 'product_id': id.id})
        elif self.name and self.reference and self.lot_name:
            id = self.env['product.product'].create({'name': self.name, 'default_code': self.reference})
            lot_id = self.env['stock.production.lot'].create({'name': self.lot_name, 'product_id': id.id})
