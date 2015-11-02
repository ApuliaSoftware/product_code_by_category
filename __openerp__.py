# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) 2015 ApuliaSoftware S.r.l. <info@apuliasoftware.it>
# All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Product Code by Category',
    'version': '0.1',
    'category': 'Product',
    'author': 'ApuliaSoftware S.r.l. <info@apuliasoftware.it>',
    'website': 'www.apuliasoftware.it',
    'license': 'AGPL-3',
    'depends': [
        'product',
    ],
    'data': [
        'views/category_view.xml',
        'views/product_view.xml',
        ],
    'active': False,
    'installable': True
}

