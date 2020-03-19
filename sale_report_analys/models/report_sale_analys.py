# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import tools
from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = "sale.report"
    

    ecart_qty = fields.Float('Ecart Qty (kg)', readonly=True)
    ecart_qtys = fields.Float('Ecart Qty (colis)', readonly=True)
    cmd_colis = fields.Float('Qty commandée (colis)', readonly=True)
    delivered_colis = fields.Float('Qty delivrée (colis)', readonly=True)
    date_de_livraison = fields.Datetime('Date de livraison', readonly=True)
    type_client = fields.Selection([('client_gros_compte', 'Client gros compte'),('client_petit_compte', 'Client petit compte')],string="Type de client", readonly=True)
    type_of_commande = fields.Selection([('commande_charc', 'Commande charcuterie'),('commande_valaille', 'Commande Volaille')],string="Type de commande", readonly=True)
    refused_command = fields.Boolean(string="CMD Refusée", readonly=True)
    user_id = fields.Many2one('hr.employee', 'Commercial', readonly=True)
    grosiste = fields.Boolean(string='Grosiste', readonly=True)
    
    def _select(self):
        select_str = """
            WITH currency_rate as (%s)
             SELECT min(l.id) as id,
                    l.product_id as product_id,
                    t.uom_id as product_uom,
                    sum(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                    sum(l.qty_delivered / u.factor * u2.factor) as qty_delivered,
                    sum(l.qty_invoiced / u.factor * u2.factor) as qty_invoiced,
                    sum(l.qty_to_invoice / u.factor * u2.factor) as qty_to_invoice,
                    sum(l.price_total / COALESCE(NULLIF(cr.rate, 0), 1.0)) as price_total,
                    sum(l.price_subtotal / COALESCE(NULLIF(cr.rate, 0), 1.0)) as price_subtotal,
                    sum(l.amt_to_invoice / COALESCE(NULLIF(cr.rate, 0), 1.0)) as amt_to_invoice,
                    sum(l.amt_invoiced / COALESCE(NULLIF(cr.rate, 0), 1.0)) as amt_invoiced,
                    count(*) as nbr,
                    s.name as name,
                    s.grosiste_cmd as grosiste,
                    sum(l.product_uom_qty / u.factor * u2.factor)-sum(l.qty_delivered / u.factor * u2.factor) as ecart_qty,
                    sum(l.secondary_uom_qty / u.factor * u2.factor)-sum((l.qty_delivered / u.factor * u2.factor)/ u3.factor) as ecart_qtys,
                    l.secondary_uom_qty as cmd_colis,
                    s.date_order as date,
                    s.confirmation_date as confirmation_date,
                    s.requested_date as date_de_livraison,
                    s.state as state,
                    s.partner_id as partner_id,
                    s.refused_command as refused_command,
                    s.vendeur as user_id,
                    s.company_id as company_id,
                    s.commande_type as type_of_commande,
                    extract(epoch from avg(date_trunc('day',s.date_order)-date_trunc('day',s.create_date)))/(24*60*60)::decimal(16,2) as delay,
                    t.categ_id as categ_id,
                    s.pricelist_id as pricelist_id,
                    s.analytic_account_id as analytic_account_id,
                    s.team_id as team_id,
                    p.product_tmpl_id,
                    partner.country_id as country_id,
                    partner.client_gc_pc as type_client,
                    partner.commercial_partner_id as commercial_partner_id,
                    sum(p.weight * l.product_uom_qty / u.factor * u2.factor) as weight,
                    sum(p.volume * l.product_uom_qty / u.factor * u2.factor) as volume
        """ % self.env['res.currency']._select_companies_rates()
        return select_str
    
    def _from(self):
        from_str = """
                sale_order_line l
                      join sale_order s on (l.order_id=s.id)
                      join res_partner partner on s.partner_id = partner.id
                        left join product_product p on (l.product_id=p.id)
                            left join product_template t on (p.product_tmpl_id=t.id)
                    left join product_uom u on (u.id=l.product_uom)
                    left join product_uom u2 on (u2.id=t.uom_id)
                    left join product_secondary_unit u3 on (u3.id=l.secondary_uom_id)
                    left join product_pricelist pp on (s.pricelist_id = pp.id)
                    left join currency_rate cr on (cr.currency_id = pp.currency_id and
                        cr.company_id = s.company_id and
                        cr.date_start <= coalesce(s.date_order, now()) and
                        (cr.date_end is null or cr.date_end > coalesce(s.date_order, now())))
        """
        return from_str
    
    def _group_by(self):
        group_by_str = """
            GROUP BY l.product_id,
                    l.order_id,
                    t.uom_id,
                    t.categ_id,
                    s.name,
                    s.date_order,
                    s.confirmation_date,
                    s.requested_date,
                    s.partner_id,
                    s.vendeur,
                    s.state,
                    s.company_id,
                    s.pricelist_id,
                    s.analytic_account_id,
                    s.team_id,
                    s.refused_command,
                    p.product_tmpl_id,
                    partner.country_id,
                    partner.client_gc_pc,
                    s.commande_type,
                    s.grosiste_cmd,
                    l.secondary_uom_qty,
                    partner.commercial_partner_id
        """
        return group_by_str