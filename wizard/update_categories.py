# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CreateBunnasiaCategoriesWizard(models.TransientModel):
    _name = "update.categories.wizard"
    _description = "Update Categories Wizard"


    product_ids = fields.Many2many('product.template', string="Product", domain=[('public_categ_ids','=', False)])
    # change_new_category = fields.Many2one('product.public.category',  string="New category")
    
    def update_category(self):
        search_product = self.env['product.template'].search([])
        if self.product_ids:
            for product in self.product_ids:
                if product.categ_id.categ_public_id:
                    product.update({'public_categ_ids':[product.categ_id.categ_public_id.id]})
                else:
                    product.update({'public_categ_ids': False})
        else:
            for product_all in search_product:
                if product_all.categ_id.categ_public_id:
                    product_all.update({'public_categ_ids':[product_all.categ_id.categ_public_id.id]})
                else:
                    product_all.update({'public_categ_ids': False})