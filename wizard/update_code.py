# -*- coding: utf-8 -*-
# © 2016 Apulia Software S.r.l. (<info@apuliasoftware.it>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, api


class UpdateProductCode(models.TransientModel):

    _name = 'update.product.code'

    @api.multi
    def update_code(self):
        products = self.env['product.product'].browse(
            self.env.context.get('active_ids', []))
        products.update_sequence()
        return {'type': 'ir.actions.act_window_close'}
