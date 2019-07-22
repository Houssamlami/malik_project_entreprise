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
    'name': "App Res Partner",

    'summary': """
         App Res Partner """,

    'description': """
        App Res Partner
    """,

    'author': "FHS Solutions",
    'website': "",
    'category': '',
    'version': '0.3',
    'depends': ['sale_management','base','crm'],

    'data': [

        'views/res_partner_views.xml',
        'views/sequences_views.xml',

    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}