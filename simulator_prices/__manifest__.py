# -*- encoding: utf-8 -*-
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Simulator prices',
    'summary': 'Simulator prices',
    'author': 'FHS Solutions',
    'license': 'AGPL-3',
    'website': '',
    'sequence': 1,
    'category': 'Product',
    'version': '1.1',
    'depends': [
        'product','base'
    ],
    'data': [
        'views/simulator_price.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    
}
