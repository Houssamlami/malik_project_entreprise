# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"
    
    
    price_avg_rate = fields.Float(compute='_compute_product_margin_fields_values', string='% de remise moyen',
        help="Pourcentage de remise moyen")
    charge_fix_margin = fields.Float(compute='_compute_product_margin_fields_values', string='% charge fixe',
        help="% charge fixe")
    charge_fix_margin_max = fields.Float(compute='_compute_product_margin_fields_values', string='% charge fixe max',
        help="% charge fixe max")
    marge_margin = fields.Float(compute='_compute_product_margin_fields_values')
    amount_charge_fix = fields.Float(compute='_compute_product_margin_fields_values', string='Montant de % charge fixe',
        help="Montant de % charge fixe")
    marge_securite_margin = fields.Float(compute='_compute_product_margin_fields_values', string='% marge de securité',
        help="% marge de securité")
    amount_marge_securite = fields.Float(compute='_compute_product_margin_fields_values', string='Valeur de marge sécurité',
        help="Valeur de marge sécurité")
    amount_refund = fields.Float(compute='_compute_product_margin_fields_values', string='Montant avoirs',
        help="Montant avoirs")
    amount_inv_total = fields.Float(compute='_compute_product_margin_fields_values', string='Montant factures',
        help="Montant factures")
    amount_refund_rate = fields.Float(compute='_compute_product_margin_fields_values', string='% avoirs',
        help="% Montant avoirs")
    sales_gap_rate = fields.Float(compute='_compute_product_margin_fields_values', string='% Ecart vente',
        help="% Ecart vente")
    commercial_rate = fields.Float(compute='_compute_product_margin_fields_values', string='% Fait commerciaux',
        help="% Fait commerciaux")
    number_sales = fields.Float(compute='_compute_product_margin_fields_values')
    number_refund = fields.Float(compute='_compute_product_margin_fields_values')
    number_sales_without_an = fields.Float(compute='_compute_product_margin_fields_values')
    number_refund_with_ref = fields.Float(compute='_compute_product_margin_fields_values')
    price_commercial = fields.Float(compute='_compute_product_margin_fields_values', string='Coût commercial')
    marge_commercial = fields.Float(compute='_compute_product_margin_fields_values', string='Marge commerciale')
    marge_commercial_rate = fields.Float(compute='_compute_product_margin_fields_values', string='% Marge commerciale')
    
    
    def _compute_product_margin_fields_values(self, field_names=None):
        res = {}
        if field_names is None:
            field_names = []
        for val in self:
            res[val.id] = {}
            date_from = self.env.context.get('date_from', time.strftime('%Y-01-01'))
            standard_price = val.product_tmpl_id.standard_price
            date_to = self.env.context.get('date_to', time.strftime('%Y-12-31'))
            invoice_state = self.env.context.get('invoice_state', 'open_paid')
            res[val.id]['date_from'] = date_from
            res[val.id]['date_to'] = date_to
            products_an = self.env.context.get('products_an')
            res[val.id]['products_an'] = products_an
            res[val.id]['invoice_state'] = invoice_state
            
            partner_id = self.env['res.partner'].search([('name', 'in', ['Atlas Négoce','ATLAS NEGOCE','Atlas Négoce GC']),('customer', '=', True)]).ids
            ids = (x.id for x in partner_id)
            
            sum_prices = val.product_tmpl_id.prix_achat + val.product_tmpl_id.prix_transport + val.product_tmpl_id.cout_avs + val.product_tmpl_id.cout_ttm
            unit_in_colis = val.product_tmpl_id.number_unit
            
            invoice_types = ()
            states = ()
            if invoice_state == 'paid':
                states = ('paid',)
            elif invoice_state == 'open_paid':
                states = ('open', 'paid')
            elif invoice_state == 'draft_open_paid':
                states = ('draft', 'open', 'paid')
            if "force_company" in self.env.context:
                company_id = self.env.context['force_company']
            else:
                company_id = self.env.user.company_id.id
                
            #############################################
            if not products_an:

            #Cost price is calculated afterwards as it is a property
                sqlstr = """
                select
                    sum(l.price_unit * l.quantity)/nullif(sum(l.quantity),0) as avg_unit_price,
                    sum(l.quantity) as num_qty,
                    sum(l.quantity * (l.price_subtotal_signed/(nullif(l.quantity,0)))) as total,
                    sum(l.quantity * pt.list_price) as sale_expected
                from account_invoice_line l
                left join account_invoice i on (l.invoice_id = i.id)
                left join product_product product on (product.id=l.product_id)
                left join product_template pt on (pt.id = product.product_tmpl_id)
                where l.price_unit != 0 and l.product_id = %s and i.state in %s and i.type IN %s and (i.date_invoice IS NULL or (i.date_invoice>=%s and i.date_invoice<=%s and i.company_id=%s))
                """
                
                sqlstrs = """
                select
                    sum(l.price_unit * l.quantity)/nullif(sum(l.quantity),0) as avg_unit_price,
                    sum(l.quantity) as num_qty,
                    sum(l.quantity * (l.price_subtotal_signed/(nullif(l.quantity,0)))) as total,
                    sum(l.quantity * pt.list_price) as sale_expected
                from account_invoice_line l
                left join account_invoice i on (l.invoice_id = i.id)
                left join product_product product on (product.id=l.product_id)
                left join product_template pt on (pt.id = product.product_tmpl_id)
                where i.partner_id.id NOT IN  %s and l.price_unit != 0 and l.product_id = %s and i.state in %s and i.type IN %s and (i.date_invoice IS NULL or (i.date_invoice>=%s and i.date_invoice<=%s and i.company_id=%s))
                """
                
                sqlstrss = """
                select
                    sum(l.price_unit * l.quantity)/nullif(sum(l.quantity),0) as avg_unit_price,
                    sum(l.quantity) as num_qty,
                    sum(l.quantity * (l.price_subtotal_signed/(nullif(l.quantity,0)))) as total,
                    sum(l.quantity * pt.list_price) as sale_expected
                from account_invoice_line l
                left join account_invoice i on (l.invoice_id = i.id)
                left join product_product product on (product.id=l.product_id)
                left join product_template pt on (pt.id = product.product_tmpl_id)
                where i.ref_livraison IS NOT NULL and l.price_unit != 0 and l.product_id = %s and i.state in %s and i.type IN %s and (i.date_invoice IS NULL or (i.date_invoice>=%s and i.date_invoice<=%s and i.company_id=%s))
                """
                
                inv_type = ('out_refund','out_refund')
                self.env.cr.execute(sqlstrss, (val.id, states, inv_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['number_refund_with_ref'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                in_type = ('out_invoice','out_invoice')
                self.env.cr.execute(sqlstrs, (partner_id, val.id, states, in_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['number_sales_without_an'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                inv_type = ('out_refund','out_refund')
                self.env.cr.execute(sqlstr, (val.id, states, inv_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['amount_refund'] = (result[2] and result[2] or 0.0)*(-1)
                res[val.id]['number_refund'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                invs_type = ('out_invoice','out_invoice')
                self.env.cr.execute(sqlstr, (val.id, states, invs_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['amount_inv_total'] = result[2] and result[2] or 0.0
                res[val.id]['number_sales'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                invoice_type = ('out_invoice', 'out_refund')
                self.env.cr.execute(sqlstr, (val.id, states, invoice_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['turnover'] = result[2] and result[2] or 0.0
                res[val.id]['charge_fix_margin'] = val.charge_fixe
                res[val.id]['marge_margin'] = val.marge
                res[val.id]['amount_charge_fix'] = res[val.id]['turnover'] * (val.charge_fixe/100)
                res[val.id]['marge_securite_margin'] = val.marge_securite
                res[val.id]['amount_marge_securite'] = res[val.id]['turnover'] * (val.marge_securite/100)
                res[val.id]['amount_refund_rate'] = res[val.id]['amount_inv_total'] and res[val.id]['amount_refund'] * 100 / res[val.id]['amount_inv_total'] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                invoice_types = ('out_invoice', 'in_refund')
                self.env.cr.execute(sqlstr, (val.id, states, invoice_types, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['sale_avg_price'] = result[0] and result[0] or 0.0
                res[val.id]['sale_num_invoiced'] = res[val.id]['number_sales_without_an'] - res[val.id]['number_refund_with_ref']
                res[val.id]['price_commercial'] = res[val.id]['sale_num_invoiced'] * sum_prices * unit_in_colis
                res[val.id]['marge_commercial'] = res[val.id]['turnover'] - res[val.id]['price_commercial']
                res[val.id]['sale_expected'] = res[val.id]['sale_num_invoiced'] * val.product_tmpl_id.list_price
                res[val.id]['sales_gap'] = res[val.id]['sale_expected'] - res[val.id]['turnover']
                res[val.id]['sales_gap_rate'] = res[val.id]['sale_expected'] and res[val.id]['sales_gap'] * 100 / res[val.id]['sale_expected'] or 0.0
                res[val.id]['commercial_rate'] = res[val.id]['sales_gap_rate'] - res[val.id]['amount_refund_rate']
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
                invoice_types = ('in_invoice', 'out_refund')
                self.env.cr.execute(sqlstr, (val.id, states, invoice_types, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['purchase_avg_price'] = result[0] and result[0] or 0.0
                res[val.id]['purchase_num_invoiced'] = result[1] and result[1] or 0.0
                res[val.id]['total_cost'] = res[val.id]['sale_num_invoiced'] * standard_price
                res[val.id]['normal_cost'] = val.standard_price * res[val.id]['sale_num_invoiced']
                res[val.id]['purchase_gap'] = res[val.id]['normal_cost'] - res[val.id]['total_cost']
            
                res[val.id]['marge_commercial_rate'] = res[val.id]['turnover'] and res[val.id]['marge_commercial'] * 100 / res[val.id]['turnover'] or 0.0
                res[val.id]['charge_fix_margin_max'] = min(res[val.id]['charge_fix_margin'],res[val.id]['marge_commercial_rate'])

                res[val.id]['total_margin'] = res[val.id]['turnover'] - res[val.id]['total_cost']
                res[val.id]['expected_margin'] = res[val.id]['sale_expected'] - res[val.id]['normal_cost']
                res[val.id]['total_margin_rate'] = res[val.id]['turnover'] and res[val.id]['total_margin'] * 100 / res[val.id]['turnover'] or 0.0
                res[val.id]['expected_margin_rate'] = res[val.id]['sale_expected'] and res[val.id]['expected_margin'] * 100 / res[val.id]['sale_expected'] or 0.0
                res[val.id]['price_avg_rate'] = val.product_tmpl_id.list_price and (val.product_tmpl_id.list_price - res[val.id]['sale_avg_price'])* 100 / val.product_tmpl_id.list_price or 0.0
                for k, v in res[val.id].items():
                    setattr(val, k, v)
            else:
                sqlstr = """
                select
                    sum(l.price_unit * l.quantity)/nullif(sum(l.quantity),0) as avg_unit_price,
                    sum(l.quantity) as num_qty,
                    sum(l.quantity * (l.price_subtotal_signed/(nullif(l.quantity,0)))) as total,
                    sum(l.quantity * pt.list_price) as sale_expected
                from account_invoice_line l
                left join account_invoice i on (l.invoice_id = i.id)
                left join product_product product on (product.id=l.product_id)
                left join product_template pt on (pt.id = product.product_tmpl_id)
                where l.price_unit != 0 and l.product_id = %s and i.state in %s and i.type IN %s and (i.date_invoice IS NULL or (i.date_invoice>=%s and i.date_invoice<=%s and i.company_id=%s))
                """
                
                sqlstrs = """
                select
                    sum(l.price_unit * l.quantity)/nullif(sum(l.quantity),0) as avg_unit_price,
                    sum(l.quantity) as num_qty,
                    sum(l.quantity * (l.price_subtotal_signed/(nullif(l.quantity,0)))) as total,
                    sum(l.quantity * pt.list_price) as sale_expected
                from account_invoice_line l
                left join account_invoice i on (l.invoice_id = i.id)
                left join product_product product on (product.id=l.product_id)
                left join product_template pt on (pt.id = product.product_tmpl_id)
                where i.partner_id.id IN  %s and l.price_unit != 0 and l.product_id = %s and i.state in %s and i.type IN %s and (i.date_invoice IS NULL or (i.date_invoice>=%s and i.date_invoice<=%s and i.company_id=%s))
                """
                
                sqlstrss = """
                select
                    sum(l.price_unit * l.quantity)/nullif(sum(l.quantity),0) as avg_unit_price,
                    sum(l.quantity) as num_qty,
                    sum(l.quantity * (l.price_subtotal_signed/(nullif(l.quantity,0)))) as total,
                    sum(l.quantity * pt.list_price) as sale_expected
                from account_invoice_line l
                left join account_invoice i on (l.invoice_id = i.id)
                left join product_product product on (product.id=l.product_id)
                left join product_template pt on (pt.id = product.product_tmpl_id)
                where i.ref_livraison IS NOT NULL and l.price_unit != 0 and l.product_id = %s and i.state in %s and i.type IN %s and (i.date_invoice IS NULL or (i.date_invoice>=%s and i.date_invoice<=%s and i.company_id=%s))
                """
                
                inv_type = ('out_refund','out_refund')
                self.env.cr.execute(sqlstrss, (val.id, states, inv_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['number_refund_with_ref'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                in_type = ('out_invoice','out_invoice')
                self.env.cr.execute(sqlstrs, (partner_id, val.id, states, in_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['number_sales_without_an'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                inv_type = ('out_refund','out_refund')
                self.env.cr.execute(sqlstr, (val.id, states, inv_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['amount_refund'] = (result[2] and result[2] or 0.0)*(-1)
                res[val.id]['number_refund'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                invs_type = ('out_invoice','out_invoice')
                self.env.cr.execute(sqlstr, (val.id, states, invs_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['amount_inv_total'] = result[2] and result[2] or 0.0
                res[val.id]['number_sales'] = result[1] and result[1] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                invoice_type = ('out_invoice', 'out_refund')
                self.env.cr.execute(sqlstr, (val.id, states, invoice_type, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['turnover'] = result[2] and result[2] or 0.0
                res[val.id]['charge_fix_margin'] = val.charge_fixe
                res[val.id]['marge_margin'] = val.marge
                res[val.id]['amount_charge_fix'] = res[val.id]['turnover'] * (val.charge_fixe/100)
                res[val.id]['marge_securite_margin'] = val.marge_securite
                res[val.id]['amount_marge_securite'] = res[val.id]['turnover'] * (val.marge_securite/100)
                res[val.id]['amount_refund_rate'] = res[val.id]['amount_inv_total'] and res[val.id]['amount_refund'] * 100 / res[val.id]['amount_inv_total'] or 0.0
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
            
                invoice_types = ('out_invoice', 'in_refund')
                self.env.cr.execute(sqlstr, (val.id, states, invoice_types, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['sale_avg_price'] = result[0] and result[0] or 0.0
                res[val.id]['sale_num_invoiced'] = res[val.id]['number_sales_without_an'] - res[val.id]['number_refund_with_ref']
                res[val.id]['price_commercial'] = res[val.id]['sale_num_invoiced'] * sum_prices * unit_in_colis
                res[val.id]['marge_commercial'] = res[val.id]['turnover'] - res[val.id]['price_commercial']
                res[val.id]['sale_expected'] = res[val.id]['sale_num_invoiced'] * val.product_tmpl_id.list_price
                res[val.id]['sales_gap'] = res[val.id]['sale_expected'] - res[val.id]['turnover']
                res[val.id]['sales_gap_rate'] = res[val.id]['sale_expected'] and res[val.id]['sales_gap'] * 100 / res[val.id]['sale_expected'] or 0.0
                res[val.id]['commercial_rate'] = res[val.id]['sales_gap_rate'] - res[val.id]['amount_refund_rate']
            
                ctx = self.env.context.copy()
                ctx['force_company'] = company_id
                invoice_types = ('in_invoice', 'out_refund')
                self.env.cr.execute(sqlstr, (val.id, states, invoice_types, date_from, date_to, company_id))
                result = self.env.cr.fetchall()[0]
                res[val.id]['purchase_avg_price'] = result[0] and result[0] or 0.0
                res[val.id]['purchase_num_invoiced'] = result[1] and result[1] or 0.0
                res[val.id]['total_cost'] = res[val.id]['sale_num_invoiced'] * standard_price
                res[val.id]['normal_cost'] = val.standard_price * res[val.id]['sale_num_invoiced']
                res[val.id]['purchase_gap'] = res[val.id]['normal_cost'] - res[val.id]['total_cost']
            
                res[val.id]['marge_commercial_rate'] = res[val.id]['turnover'] and res[val.id]['marge_commercial'] * 100 / res[val.id]['turnover'] or 0.0
                res[val.id]['charge_fix_margin_max'] = min(res[val.id]['charge_fix_margin'],res[val.id]['marge_commercial_rate'])

                res[val.id]['total_margin'] = res[val.id]['turnover'] - res[val.id]['total_cost']
                res[val.id]['expected_margin'] = res[val.id]['sale_expected'] - res[val.id]['normal_cost']
                res[val.id]['total_margin_rate'] = res[val.id]['turnover'] and res[val.id]['total_margin'] * 100 / res[val.id]['turnover'] or 0.0
                res[val.id]['expected_margin_rate'] = res[val.id]['sale_expected'] and res[val.id]['expected_margin'] * 100 / res[val.id]['sale_expected'] or 0.0
                res[val.id]['price_avg_rate'] = val.product_tmpl_id.list_price and (val.product_tmpl_id.list_price - res[val.id]['sale_avg_price'])* 100 / val.product_tmpl_id.list_price or 0.0
                for k, v in res[val.id].items():
                    setattr(val, k, v)
        return res