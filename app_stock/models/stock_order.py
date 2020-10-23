# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError

from odoo.tools.misc import formatLang
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.addons import decimal_precision as dp

from datetime import datetime, timedelta
from datetime import datetime
import datetime
import dateutil.parser



class StockPicking(models.Model):
    _inherit = "stock.picking"

    total_weight_stock_sec_auto = fields.Float(string='Total sec', compute='_compute_weight_total_stock_sec')
    total_weight_stock_frais_auto = fields.Float(string='Total frais)', compute='_compute_weight_total_stock_frais')
    total_weight_stock_surg_auto = fields.Float(string='Total surg)', compute='_compute_weight_total_stock_surg')
    total_weight_stock_volailles_auto = fields.Float(string='Total volailles)', compute='_compute_weight_total_stock_volailles')
    total_colis_delivered = fields.Float(string='Total Colis', compute='_compute_colis_poids_total_bl')
    total_weight_delivered = fields.Float(string='Poids Total', compute='_compute_colis_poids_total_bl', track_visibility='onchange')
    is_return_picking = fields.Boolean(string="Is Retour", compute='get_is_return_picking')
    name_provisoir = fields.Char(string="Nom Provisoir", compute='get_is_return_picking')
    number_product_to_deliver = fields.Float(string='Produits à livrer', compute='_compute_number_product_to_deliver')
    expediteur_in_picking = fields.Selection([('MV', 'Malik V'), ('An', 'Atlas N')], related='sale_id.Expediteur', string="Expediteur")
    bl_supplier = fields.Char(string="N° BL fournisseur")
    origin_command = fields.Char(string="La commande origine", index=True, states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    #typeprod = fields.Char(string="Nature prod", compute='get_nature_prod', store='true')
    typeproduit = fields.Char(related='sale_id.produitalivrer' ,string="Nature produit")
    
    
    @api.one      
    def _compute_number_product_to_deliver(self):
        for record in self:
            pickings = self.env['stock.picking'].search([('partner_id', '=', self.partner_id.id),('picking_type_code','=','outgoing'),('state','!=','cancel')])
            cmpt = 0
            for picking in pickings:
                if dateutil.parser.parse(picking.scheduled_date).date() == dateutil.parser.parse(record.scheduled_date).date():
                    for move in picking.move_lines:
                        cmpt += move.secondary_uom_qty
            record.number_product_to_deliver = cmpt
            
    '''def get_nature_prod(self):
        typeprodt=''
        for record in self:
            if record.origin:
                sale = self.env['sale.order'].search([('name', '=', record.origin)])
                for info in sale:
                    typeprodt=info.produitalivrer
                record.typeprod = typeprodt'''
            
    
    
    def get_is_return_picking(self):
        for record in self:
            SO = 'SO'
            PO = 'PO'
            char = ''
            char = record.group_id.name
            if char != False:
                if (char.find(SO) != -1 and record.picking_type_id.code == 'incoming') or (char.find(PO) != -1 and record.picking_type_id.code == 'outgoing'):
                    record.is_return_picking = True
                    string = ''
                    string = record.name
                    print(string)
                    record.name_provisoir = string.replace('Bon de Réception','BRT')
                    print(record.name_provisoir)
                else:
                    record.is_return_picking = False
                
    def _compute_colis_poids_total_bl(self):
        for picking in self:
            total_colis = 0
            total_poids = 0
            for line in picking.move_lines:
                if line.product_id and line.product_id.uom_id.name != 'kg':
                    total_poids += (line.quantity_done or 0.0)*line.product_id.weight
                    if line.quantity_done != 0.0:
                        total_colis += (line.secondary_uom_qty)
                if line.product_id and line.product_id.uom_id.name == 'kg':
                    total_poids += (line.quantity_done or 0.0)
                    if line.quantity_done != 0.0:
                        total_colis += (line.secondary_uom_qty or 0.0)
            picking.total_weight_delivered = total_poids
            picking.total_colis_delivered = total_colis
            
    @api.multi
    def print_br_stock_empty(self):
        return self.env.ref('app_stock.report_br_stock_empty').report_action(self)

    def _compute_weight_total_stock_sec(self):
        for stock in self:
            weight_stock_sec = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name =="Sec":
                    weight_stock_sec += line.product_uom_qty  or 0.0
            stock.total_weight_stock_sec_auto = weight_stock_sec

    def _compute_weight_total_stock_frais(self):
        for stock in self:
            weight_stock_frais = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name == "Frais":
                    weight_stock_frais += line.product_uom_qty  or 0.0
            stock.total_weight_stock_frais_auto = weight_stock_frais

    def _compute_weight_total_stock_surg(self):
        for stock in self:
            weight_stock_surg = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name == "Surgelé":
                    weight_stock_surg += line.product_uom_qty  or 0.0
            stock.total_weight_stock_surg_auto = weight_stock_surg

    def _compute_weight_total_stock_volailles(self):
        for stock in self:
            weight_stock_volailles = 0
            for line in stock.move_lines:
                if line.product_id.Androit_stockage.name == "Volailles":
                    weight_stock_volailles += line.product_uom_qty  or 0.0
            stock.total_weight_stock_volailles_auto = weight_stock_volailles
    
    '''@api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(StockPicking, self).fields_view_get(
            view_id=view_id,
            view_type=view_type,
            toolbar=toolbar,
            submenu=submenu)
        active_model = self.env.context.get('active_model')
        picking_id = self.env.context.get('active_id')
        if res.get('fields').get('state')['selection'][0][1] == 'confirmed':
            if res.get('toolbar', False) and res.get('toolbar').get('print', False):
                reports = res.get('toolbar').get('print')
                for report in reports:
                    if report.get('report_file', False) and report.get('report_file') == 'app_stock.report_br_stock_empty':
                        res['toolbar']['print'].remove(report)
        return res'''
            
    @api.multi
    def button_validate(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some lines to move'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_('You cannot validate a transfer if you have not processed any quantity. You should rather cancel the transfer.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a lot/serial number for %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_overprocessed_check'):
            view = self.env.ref('stock.view_overprocessed_transfer')
            wiz = self.env['stock.overprocessed.transfer'].create({'picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_done()
        #//////////////////////////////////////////////////////////////
        for mov_lines in self.move_lines:
            if self.picking_type_code == 'outgoing':
                print('stock move internal')
                qty = mov_lines.product_id.secondary_unit_qty_available
            #res.qty_available = qty
                mov_lines.product_id.secondary_unit_qty_available += mov_lines.secondary_uom_qty
            
            elif self.picking_type_code == 'incoming':
                print('stock move customer')
                qty = mov_lines.product_id.secondary_unit_qty_available
                print(qty)
                #res.qty_available = qty
                mov_lines.product_id.secondary_unit_qty_available -= mov_lines.secondary_uom_qty
                print(mov_lines.product_id.secondary_unit_qty_available)
                print(mov_lines.secondary_uom_qty)
            
            else:
                mov_lines.product_id.secondary_unit_qty_available -= 0
        #//////////////////////////////////////////////////////////////
        return
            
            
class StockProductionLot(models.Model):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'
    
    
    @api.depends('product_qty')
    def _compute_stock_not_empty(self):
        for lot in self:
            if lot.product_qty > 0:
                lot.stock_not_empty = True
            else:
                lot.stock_not_empty = False
            print(lot.stock_not_empty)
            
             
    date_refer = fields.Datetime(string="Date référence", default=fields.Date.today())
    char_expiration = fields.Char(default='Expiration Alert', string="Alerte d'expiration de produit")
    product_removal_alert = fields.Boolean(compute='_compute_product_use_removal_alerts', string="Alerte Retrait")
    product_use_alert = fields.Boolean(compute='_compute_product_use_removal_alerts', string=u"Alerte Limite d'utilisation")
    stock_qty_lot = fields.Float(string=u"Qty lot", compute='_product_qty_in_lot', store=True)
    
    @api.one
    @api.depends('product_qty','quant_ids.quantity')
    def _product_qty_in_lot(self):
        quants = self.quant_ids.filtered(lambda q: q.location_id.usage in ['internal', 'transit'])
        self.stock_qty_lot = sum(quants.mapped('quantity'))
        
        
    @api.depends('removal_date','use_date')
    def _compute_product_use_removal_alerts(self):
        current_date = fields.Datetime.now()
        for lot in self.filtered(lambda l: l.removal_date):
            lot.product_removal_alert = lot.removal_date <= current_date
        for lots in self.filtered(lambda l: l.use_date):
            lots.product_use_alert = lots.use_date <= current_date
    
    
    def _get_datttes(self, product_id=None):
        """Returns dates based on number of days configured in current lot's product."""
        mapped_fields = {
            'life_date': 'life_time',
            'use_date': 'use_time',
            'removal_date': 'removal_time',
            'alert_date': 'alert_time'
        }
        
        str_date = str(self.date_refer)
        date_r = datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
        res = dict.fromkeys(mapped_fields, False)
        product = self.env['product.product'].browse(product_id) or self.product_id
        if product:
            i=0
            for field in mapped_fields:
                duration = getattr(product, mapped_fields[field])
                if duration and field != 'life_date':
                    date = date_r + datetime.timedelta(days=duration)
                    res[field] = fields.Datetime.to_string(date)              
                if field == 'life_date':
                    date = date_r + datetime.timedelta(days=0)
                    res[field] = fields.Datetime.to_string(date)
                i = i+1
        return res
    
    def _get_dattes(self, product_id=None,date=None):
        """Returns dates based on number of days configured in current lot's product."""
        mapped_fields = {
            'life_date': 'life_time',
            'use_date': 'use_time',
            'removal_date': 'removal_time',
            'alert_date': 'alert_time'
        }
        
        str_date = str(date)
        print(str_date)
        date_r = datetime.datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')
        res = dict.fromkeys(mapped_fields, False)
        product = self.env['product.product'].browse(product_id) or self.product_id
        if product:
            i=0
            for field in mapped_fields:
                duration = getattr(product, mapped_fields[field])
                if duration and field != 'life_date':
                    date = date_r + datetime.timedelta(days=duration)
                    res[field] = fields.Datetime.to_string(date)              
                if field == 'life_date':
                    date = date_r + datetime.timedelta(days=0)
                    res[field] = fields.Datetime.to_string(date)
                i = i+1
        return res
    
    
    
    @api.model
    def create(self, values):
        
        date = values.get('date_refer')
        dates = self._get_dattes(values.get('product_id') or self.env.context.get('default_product_id'), date)
        for d in dates:
            if not values.get(d):
                values[d] = dates[d]
        lot = super(StockProductionLot, self).create(values)  
        return lot
    
    @api.onchange('date_refer')
    def _onchange_date_refer(self):
        dates_dict = self._get_datttes()
        for field, value in dates_dict.items():
            setattr(self, field, value)
            
    '''@api.onchange('product_expiry_alert')
    @api.depends('product_expiry_alert')
    def _notif_expiration_lot(self):
        for record in self:
            if record.product_expiry_alert:
                activity = self.env['mail.activity'].sudo().create({
                        'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                        'note': _('Expired lot. '),
                        'res_id': record.id,
                        'res_model_id': self.env.ref('stock.model_stock_production_lot').id,
                        })
                activity._onchange_activity_type_id()
            

class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    _description = 'Return Picking'
    
    @api.multi
    def _create_returns(self):
        new_picking, pick_type_id = super(ReturnPicking, self)._create_returns()
        picking = self.env['stock.picking'].browse(new_picking)
        picking.update({'is_return_picking': True,
                       })
        return new_picking, pick_type_id'''