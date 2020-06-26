# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
import logging
from itertools import groupby
from odoo import models, api, fields, _, exceptions
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools import float_compare, float_round, float_repr
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

             
    '''         
    @api.depends('order_line.price_subtotal')
    def _get_prix_transport(self):
        for record in self:
            obj = self.env['purchase.order.line'].search([('order_id', '=', record.id)], limit=1)
            if len(obj) != 0:            
                record.prix_transp = obj.price_subtotal
                
                
    @api.depends('kilometre','prix_transp')
    def _get_prix_par_km(self):
        for record in self:
            precision = self.env['decimal.precision'].precision_get('Product Price')
            if record.kilometre != 0:
                record.prix_par_km = float_round(record.prix_transp/record.kilometre, precision_digits=precision)
            
    @api.depends('qty_totals','prix_transp')
    def _get_prix_par_kg(self):
        for record in self:
            precision = self.env['decimal.precision'].precision_get('Product Price')
            if record.qty_totals != 0:
                record.prix_par_kg = float_round(record.prix_transp/record.qty_totals, precision_digits=precision)
                
    @api.depends('order_line.product_id')
    def _get_km(self):
        for record in self:
            obj = self.env['purchase.order.line'].search([('order_id', '=', record.id)], limit=1)
            if len(obj) != 0:            
                record.kilometre = obj.km
    
             
        
    @api.multi
    @api.depends('purchase_order_id')
    def _get_totals_qty(self):
        for record in self:
            cmpt = 0
            if record.purchase_order_id:
                obj = self.env['purchase.order'].search([('id', '=', record.purchase_order_id.id)])
                for lines in obj.order_line:
                    if lines.product_id:
                        cmpt += lines.product_qty
            record.qty_totals = cmpt
    ''' 
    
    @api.depends('state', 'order_line.qty_invoiced', 'order_line.qty_received', 'order_line.product_qty','invoice_ids')
    def _get_stat_invoice(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for order in self:
            if order.state not in ('purchase', 'done'):
                order.invoice_statu = 'no'
                continue

            if any(float_compare(line.qty_invoiced, line.product_qty if line.product_id.purchase_method == 'purchase' else line.qty_received, precision_digits=precision) >= 0 for line in order.order_line) and order.invoice_ids and order.invoice_ids[0].state not in ('paid'):
                order.invoice_statu = 'to invoice'
            elif all(float_compare(line.qty_invoiced, line.product_qty if line.product_id.purchase_method == 'purchase' else line.qty_received, precision_digits=precision) >= 0 for line in order.order_line) and order.invoice_ids and order.invoice_ids[0].state in ('paid'):
                order.invoice_statu = 'invoiced'
            else:
                order.invoice_statu = 'no'  
        
    @api.onchange('order_line.price_unit')
    def _on_change_orderline(self):
         for record in self:
             record._get_totals_qty()
    
    @api.onchange('purchase_order_id')
    def _on_change_purchaseorderid(self):
        for record in self:
            record._get_totals_qty()
    
    state = fields.Selection([
        ('draft', u'Commande Brouillon'),
        ('sent', u'Commande Envoyée'),
        ('to approve', u'À approuver'),
        ('purchase', 'Commande Fournisseur'),
        ('done', u'Bloqué'),
        ('cancel', u'Annulée')
        ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    invoice_statu = fields.Selection([
        ('no', 'A facturer'),
        ('to invoice', 'Non payée'),
        ('invoiced', 'Payée'),
        ], string='État de facture', compute='_get_stat_invoice', store=True, readonly=True, copy=False, default='no')
    semaine = fields.Char(string="Semaine")
    abattage = fields.Char(string="Abattage", track_visibility='always')
    qty_totals = fields.Float(string=u"Quantité Transportée(KG)", track_visibility='onchange')
    logistic = fields.Boolean(string="Logistic")
    data_file_cmr = fields.Binary(string='Fichier CMR')
    nbr_camions = fields.Float(string='Nombre de Camions')
    tonnage = fields.Float(string="Tonnage par camion", default=21000)
    palette = fields.Float(string="Nombre de palette par camion", default=32)
    po_invoiced = fields.Boolean(string="Facturée", track_visibility='onchange')
    po_to_invoice = fields.Boolean(string="A facturer", track_visibility='onchange')
    #purchase_order_id = fields.Many2one(comodel_name='purchase.order', string=u'BC Achat', domain=[('partner_id.name', 'in', ('IMEX','BONA'))])
    
    @api.model
    def default_get(self, fields):
        res = super(PurchaseOrder, self).default_get(fields)
        if self.env.user.has_group('app_purchase_order.group_achat_logistique'):
            res.update({'logistic': True})
        else:
            res.update({'logistic': False})
        return res
    
    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            #purchase command must have destination in each POL before validation
            if not order.logistic and any(line.location_dest_id.id is False for line in order.order_line):
                raise UserError(_("Merci de remplir toute les destinations."))
            #logistic command must have file CMR before validation 
            if order.logistic and not order.data_file_cmr:
                raise UserError(_("Merci de joindre un fichier CMR."))
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step'\
                    or (order.company_id.po_double_validation == 'two_step'\
                        and order.amount_total < self.env.user.company_id.currency_id.compute(order.company_id.po_double_validation_amount, order.currency_id))\
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True
    
    @api.model
    def _prepare_picking(self, location):
        if not self.group_id:
            self.group_id = self.group_id.create({
                'name': self.name,
                'partner_id': self.partner_id.id
            })
        if not self.partner_id.property_stock_supplier.id:
            raise UserError(_("You must set a Vendor Location for this partner %s") % self.partner_id.name)
        return {
            'picking_type_id': self.picking_type_id.id,
            'partner_id': self.partner_id.id,
            'date': self.date_order,
            'origin': self.name,
            'location_dest_id': location.id,
            'location_id': self.partner_id.property_stock_supplier.id,
            'company_id': self.company_id.id,
        }
    
    @api.multi
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        for order in self:
            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                print (order.order_line.mapped('location_dest_id'))
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done','cancel'))
                for location in order.order_line.mapped('location_dest_id'):
                    if not pickings:
                        res = order._prepare_picking(location)
                        picking = StockPicking.create(res)
                    else:
                        picking = pickings[0]
                    moves = order.order_line.filtered(lambda x: x.location_dest_id.id == location.id)._create_stock_moves(picking)
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()
                    picking.message_post_with_view('mail.message_origin_link',
                        values={'self': picking, 'origin': order},
                        subtype_id=self.env.ref('mail.mt_note').id)
            
        return True


    @api.model
    def create(self, vals):
        purchase = super(PurchaseOrder,self).create(vals)
        if purchase.logistic == True:
            if any(not line.account_analytic_id for line in purchase.order_line):
                raise exceptions.ValidationError(_('Remplir les destinations finales !'))
                return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }
        return purchase
    '''
    @api.multi
    def write(self, vals):
      #  if vals['logistic'] == 'true':
            if any(not line.account_analytic_id for line in self.order_line):
                raise exceptions.ValidationError(_('Remplir les destinations finales !'))
                return {
                        'warning': {'title': _('Error'), 'message': _('Error message'),},
                        }  
        purchase = super(PurchaseOrder,self).write(vals) 
        return purchase
        '''