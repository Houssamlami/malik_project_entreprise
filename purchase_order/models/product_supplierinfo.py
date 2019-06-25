# -*- coding: utf-8 -*-
# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

import logging
from itertools import groupby
from odoo import models, api, fields, _

_logger = logging.getLogger(__name__)


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"
    
    nbr_km = fields.Integer(string='KM')