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


from openerp import models, api


class UpdateProductCode(models.TransientModel):

    _name = 'update.product.code'

    @api.multi
    def update_code(self):
        products = self.env['product.product'].browse(
            self.env.context.get('active_ids', []))
        products.update_sequence()
        return {'type': 'ir.actions.act_window_close'}


class UpdateTemplateCode(models.TransientModel):

    _name = 'update.template.code'

    @api.multi
    def update_code(self):
        templates = self.env['product.template'].browse(
            self.env.context.get('active_ids', []))
        templates.update_sequence()
        return {'type': 'ir.actions.act_window_close'}
