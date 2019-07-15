# -*- coding: utf-8 -*-
# Copyright 2014-2016 Numerigraphe SARL
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale report Analysis",
    "version": "11.0.1.0.0",
    "summary": "Sale report Analysis",
    "author": "FHS Solution",
    "website": "",
    "category": "Sale Management",
    "license": "AGPL-3",
    "depends": [
        'base',"sale","sale_management",'product',
    ],
    "data": [
        #"views/report_sale_analys.xml"
        'views/tree_view_top_customer_view.xml',
        'wizard/top_sales_view.xml',
        'report/selected_product_report.xml',
        'report/selected_product_template.xml',
        'report/selected_product_amount_report.xml',
        'report/selected_product_amount_template.xml',
        'wizard/wizard_top_customers_view.xml',
    ],
    "installable": True,
    "application": False,
}
