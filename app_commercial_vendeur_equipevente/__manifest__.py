# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright © 2016 Moulay rachid hachimi. (<http://Moulay rachid hachimi>).
# 
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "commercial_vendeur_equipevente",

    'summary': """
         Add commercial_vendeur_equipevente """,

    'description': """
        Add commercial_vendeur_equipevente v1
    """,

    'author': "Najlae",
    'website': "najlae.info",
    'category': 'Helpser_product ',
    'version': '0.3',
    'depends': ['sale_management','base','crm'],

    'data': [

        'views/commercial_vendeur_equipevente.xml',

    ],
    'application': 'True'
}