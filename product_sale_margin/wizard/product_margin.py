# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import api, fields, models, _


class ProductMargin(models.TransientModel):
    _inherit = 'product.margin'
    _description = 'Product Margin'

    products_an = fields.Boolean('Produits AN', default=False)
    
    @api.multi
    def action_open_window(self):
        self.ensure_one()
        context = dict(self.env.context or {})

        def ref(module, xml_id):
            proxy = self.env['ir.model.data']
            return proxy.get_object_reference(module, xml_id)

        model, search_view_id = ref('product', 'product_search_form_view')
        model, graph_view_id = ref('product_margin', 'view_product_margin_graph')
        model, form_view_id = ref('product_margin', 'view_product_margin_form')
        model, tree_view_id = ref('product_margin', 'view_product_margin_tree')

        context.update(invoice_state=self.invoice_state)
        context.update(products_an=self.products_an)

        if self.from_date:
            context.update(date_from=self.from_date)

        if self.to_date:
            context.update(date_to=self.to_date)

        views = [
            (tree_view_id, 'tree'),
            (form_view_id, 'form'),
            (graph_view_id, 'graph')
        ]
        return {
            'name': _('Product Margins'),
            'context': context,
            'view_type': 'form',
            "view_mode": 'tree,form,graph',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'views': views,
            'view_id': False,
            'search_view_id': search_view_id,
        }