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


from openerp import models, fields, api, SUPERUSER_ID


class ProductCategory(models.Model):

    _inherit = 'product.category'

    code = fields.Char(size=10)
    sequence_id = fields.Many2one('ir.sequence', ondelete='cascade')
    use_sequence = fields.Boolean('Use Sequence')
    prefix_code = fields.Char(compute='_prefix_code', store=True)

    @api.multi
    def create_sequence(self, vals):
        # Create new no_gap entry sequence for every new category
        name = ''
        if vals.get('name', False):
            name = vals['name']
        if vals.get('code', False):
            name = '[%s] %s' % (vals['code'], name)
        if vals.get('parent_id', False):
            parent = self.browse(vals['parent_id']).name_get()
            name = '%s / %s' % (parent[0][1], name)
        sequence_code = self.env['ir.sequence.type'].search(
            [('code', '=', 'product.code.by.category')]) or ''
        if sequence_code:
            sequence_code = sequence_code.code
        seq = {
            'name': name,
            'implementation': 'no_gap',
            'padding': 4,
            'number_increment': 1,
            'code': sequence_code,
        }
        return self.env['ir.sequence'].create(seq)

    @api.model
    def create(self, vals):
        if not vals.get('sequence_id', False) and vals.get('use_sequence',
                                                           False):
            seq_id = self.sudo().create_sequence(vals)
            vals.update({'sequence_id': seq_id.id})
        return super(ProductCategory, self).create(vals)

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        # OVERRIDE STANDARD NAME_GET
        reads = self.read(['name', 'code', 'parent_id'])
        res = []
        for record in reads:
            name = record['name']
            if record['code']:
                name = '[%s] %s' % (record['code'], name)
            if record['parent_id']:
                parent_name = record['parent_id'][1]
                name = '%s / %s' % (parent_name, name)
            res.append((record['id'], name))
        return res

    @api.one
    @api.depends('code', 'parent_id')
    def _prefix_code(self):
        code = self.code or ''
        if self.parent_id:
            parent_code = self.parent_id.prefix_code or ''
            code = '%s%s' % (parent_code, code)
        self.prefix_code = code

    @api.model
    def name_search(self, name='', args=None, operator='ilike', context=None,
                    limit=100):
        res = super(ProductCategory, self).name_search(
            name, args, operator, limit=limit, context=context)
        if not name:
            return res
        codes = self.search([
            ('prefix_code', operator, name)])
        if not codes:
            return res
        for code in codes:
            res += code.name_get()
        return res

    def get_product_sequence(self):
        category = self
        code = ''
        # ----- Valid only for categories with active sequence
        if category.use_sequence and category.sequence_id:
            sequence_model = self.env['ir.sequence']
            code = '{prefix_code}{sequence}'
            code = code.format(
                prefix_code=category.prefix_code,
                sequence=sequence_model.next_by_id(category.sequence_id.id))
        return code


class ProductTemplate(models.Model):

    _inherit = 'product.template'

    @api.multi
    def update_sequence(self):
        product_model = self.env['product.product']
        for template in self:
            values = product_model._get_sequence_vals({
                'product_tmpl_id': template.id,
                })
            if values.get('default_code', ''):
                template.write(values)
        return True


class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _get_sequence_vals(self, values):
        categ_id = False
        if values.get('categ_id', False) and not values.get('default_code', ''):
            categ_id = values['categ_id']
        elif values.get('product_tmpl_id', False):
            categ_id = self.env['product.template'].browse(
                values['product_tmpl_id']).categ_id.id
        if categ_id:
            category = self.env['product.category'].browse(categ_id)
            # ----- Try to get the code from category
            default_code = category.get_product_sequence()
            # ------ If category exists, update product code
            if default_code:
                # ----- check if code exist
                if self.env['product.product'].search([('default_code',
                                                        '=', default_code)]):
                    raise Exception('The code %s already exists', default_code)
                values.update({
                    'default_code': default_code, })
        return values

    @api.multi
    def update_sequence(self):
        for product in self:
            values = product._get_sequence_vals({
                'categ_id': product.categ_id.id,
                })
            if values.get('default_code', ''):
                product.write(values)
        return True

    @api.model
    def create(self, values):
        # ----- Create the product code
        if not values.get('default_code', False):
            values = self._get_sequence_vals(values)
        return super(ProductProduct, self).create(values)
