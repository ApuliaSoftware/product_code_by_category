# -*- coding: utf-8 -*-
# © 2016 Apulia Software S.r.l. (<info@apuliasoftware.it>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp.tests.common import TransactionCase


class TestProductCode(TransactionCase):

    def _create_category_parent(self):
        return self.env['product.category'].create({
            'name': 'Parent',
            'code': 'DAD'})

    def _create_category_child(self):
        return self.env['product.category'].create({
            'name': 'Child',
            'parent_id': self.category_parent.id,
            'code': 'CHILD',
            'use_sequence': True,
        })

    def _create_product(self):
        return self.env['product.product'].create({
            'name': 'My Product',
            'categ_id': self.category_child.id,
        })

    def _create_product2(self):
        return self.env['product.product'].create({
            'name': 'Wrong Code',
            'categ_id': self.category_child.id,
            'default_code': 'MYCODE'
        })

    def setUp(self):
        super(TestProductCode, self).setUp()
        self.category_parent = self._create_category_parent()
        self.category_child = self._create_category_child()
        self.product = self._create_product()
        self.product2 = self._create_product2()

    def test_parent_no_sequence(self):
        self.assertFalse(self.category_parent.sequence_id.id)

    def test_child_sequence(self):
        self.assertTrue(self.category_child.sequence_id.id)
        self.assertEqual(self.category_child.prefix_code, 'DADCHILD')

    def test_product_code(self):
        product = self.product
        self.assertEqual(product.default_code, 'DADCHILD0001')

    def test_update_product_code(self):
        product = self.product2
        product.update_sequence()
        self.assertEqual(product.default_code, 'DADCHILD0002')

    def test_wizard_update_code(self):
        product = self.product2
        wizard = self.env['update.product.code'].with_context(
            active_ids=[product.id]).create({})
        wizard.update_code()
        self.assertEqual(product.default_code, 'DADCHILD0002')

    def test_write_sequence_on_category(self):
        my_category = self.env['product.category'].create({
            'name': 'Child',
            'parent_id': self.category_parent.id,
            'code': 'CHILD',
        })
        my_category.write({'use_sequence': True})
        self.assertTrue(my_category.sequence_id.id)

    def test_assign_existing_sequence(self):
        my_category = self.env['product.category'].create({
            'name': 'Child',
            'parent_id': self.category_parent.id,
            'code': 'CHILD',
        })
        sequence_code = self.env['ir.sequence.type'].search(
            [('code', '=', 'base.product.auto.sequence')]) or ''
        if sequence_code:
            sequence_code = sequence_code.code
        seq = {
            'name': 'Child',
            'implementation': 'no_gap',
            'padding': 4,
            'number_increment': 1,
            'code': sequence_code,
        }
        sequence = self.env['ir.sequence'].create(seq)
        my_category.write({'use_sequence': True})
        self.assertEqual(sequence.id, my_category.sequence_id.id)

