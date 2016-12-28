# -*- coding: utf-8 -*-
# © 2016 Apulia Software S.r.l. (<info@apuliasoftware.it>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields, api, _
import re
from openerp.exceptions import Warning as UserError


class ProductCategory(models.Model):

    _inherit = 'product.category'

    code = fields.Char(size=10)
    sequence_id = fields.Many2one('ir.sequence', ondelete='cascade')
    use_sequence = fields.Boolean('Use Sequence')
    prefix_code = fields.Char(compute='_prefix_code', store=True)

    @api.multi
    def create_sequence(self, record):
        # Create new no_gap entry sequence for every new category
        name = record.name_get()[0][1]
        sequence_code = self.env['ir.sequence.type'].search(
            [('code', '=', 'base.product.auto.sequence')]) or ''
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
        res = super(ProductCategory, self).create(vals)
        if not res.sequence_id and res.use_sequence:
            seq_id = res.sudo().create_sequence(res)
            res.sequence_id = seq_id.id
        return res

    @api.multi
    def write(self, vals):
        res = super(ProductCategory, self).write(vals)
        for cat in self:
            seq_id = self.sequence_id
            if not cat.sequence_id and cat.use_sequence:
                name = cat.name_get()[0][1]
                seq_id = cat.env['ir.sequence'].search([('name', '=', name)])
                if not seq_id:
                    seq_id = cat.sudo().create_sequence(cat)
                cat.sequence_id = seq_id.id
            if seq_id:
                cat.update_cat_seq_name(cat, seq_id)
        return res

    @api.multi
    def name_get(self):
        def get_names(cat):
            """ Return the list [cat.name, cat.parent_id.name, ...] """
            res = []
            while cat:
                if cat.code:
                    res.append('[{code}] {name}'.format(
                        code=cat.code, name=cat.name))
                else:
                    res.append('{name}'.format(name=cat.name))
                cat = cat.parent_id
            return res

        return [(cat.id, " / ".join(reversed(get_names(cat)))) for cat in self]

    @api.one
    @api.depends('code', 'parent_id', 'parent_id.code')
    def _prefix_code(self):
        code = self.code or ''
        if self.parent_id:
            parent_code = self.parent_id.prefix_code or ''
            code = '%s%s' % (parent_code, code)
        self.prefix_code = code

    @api.model
    def name_search(self, name='', args=None, operator='ilike', context=None,
                    limit=100):
        name = re.sub(r"\[\w+\] ", "", name)
        res = super(ProductCategory, self).name_search(
            name, args, operator, limit=limit, context=context)
        if not name:
            return res
        list_id = []
        for tpl in res:
            list_id.append(tpl[0])
        codes = self.search([
            ('prefix_code', operator, name),
            ('id', 'not in', list_id)
        ])
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

    def update_cat_seq_name(self, cat, seq):
        seq.name = cat.name_get()[0][1]

class ProductProduct(models.Model):

    _inherit = 'product.product'

    def _get_sequence_vals(self, values):
        categ_id = False
        if values.get('categ_id', False) \
                and not values.get('default_code', ''):
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
                    raise UserError(
                        _('The code {} already exists'.format(default_code)))
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
        """
            Create the product code (based on Customer standard)
            if user create a new product
        """
        if not values.get('default_code', False):
            values = self._get_sequence_vals(values)
        product = super(ProductProduct, self).create(values)
        return product
