# -*- coding: utf-8 -*-
# Copyright 2014-2016 Numerigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Purchase report Analysis",
    "version": "11.0.1.0.0",
    "summary": "Purchase report Analysis",
    "author": "FHS Solution",
    "website": "",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "depends": [
        'base',"purchase",'product',
    ],
    "data": [
        "report/purchase_report_views.xml"
        
    ],
    "installable": True,
    "application": False,
}
