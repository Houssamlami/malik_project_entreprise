# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    secondary_uom_ids = fields.One2many(
        comodel_name='product.secondary.unit',
        inverse_name='product_tmpl_id',
        string='BOX type',
        help='Default box type.',
    )
    sale_secondary_uom_id = fields.Many2one(
        comodel_name='product.secondary.unit',
        string='Default unit sale',
    )
