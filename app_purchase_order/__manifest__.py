# -*- coding: utf-8 -*-
# Copyright 2014-2016 Numérigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "App Malik Purchase",
    "version": "11.0.1.0.0",
    "summary": "App Malik Purchase",
    "author": "FHS Solutions",
    "website": "",
    "category": "Purchase",
    "license": "AGPL-3",
    "depends": [
        "purchase",'base'
    ],
    "data": [
        "views/purchase_order_views.xml",
        'views/report_purchase_order.xml',
    ],
    "installable": True,
    "application": False,
}
