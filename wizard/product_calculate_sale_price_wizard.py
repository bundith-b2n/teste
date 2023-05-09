# -*- coding: utf-8 -*-
from email.policy import default
from odoo import api, fields, models, _
from datetime import datetime
import math
from odoo.exceptions import ValidationError, UserError

class ProductCategoryPrice(models.Model):
    _name = "lod.product.category.price"
    _description = "Product Category Wizard"

    categ_id = fields.Many2one('product.category', string='Product Category')
    name = fields.Char('Name', related='categ_id.display_name')
    margin_percent = fields.Float('Margin Percent')

class ProductCategoryBatchPriceWizard(models.TransientModel):
    _name = "product.categ.batch.price.wizard"
    _description = "Product Category Batch Price Wizard"
    
    def roundup_amount(self, amount):
        fee = str(amount)		

        last_three = fee[-3:]   
        if int(last_three) <= 200 and int(last_three) > 0:
            return int(math.ceil(amount / 500.0)) * 500 - 500
        elif int(last_three) > 200 and int(last_three) <= 500:
            return int(math.ceil(amount / 500.0)) * 500
        elif int(last_three) > 500 and int(last_three) <= 700:
            return int(math.ceil(amount / 500.0)) * 500 - 500
        elif int(last_three) > 700 and int(last_three) <= 999:
            return int(math.ceil(amount / 500.0)) * 500
        else:
            return math.ceil(amount)

    price_calc_option = fields.Selection([
        ('imp_country', 'Country Import'),
        ('prod_category', 'Product Category'),
    ], string='Price Calculate Option')
    pro_categ_ids = fields.Many2many('lod.product.category.price', string='Product Category')

    def action_confirm_calculate(self):
        for prod_categ in self.pro_categ_ids:
            # print('===prod_categ===>',prod_categ.categ_id)
            categ_id = self.env['product.category'].search([('parent_path','ilike', '/'+str(prod_categ.categ_id.id)+'/')])
            product_id = self.env['product.template'].search([('categ_id','in', categ_id.ids)])
            for product in product_id:
                if product.new_cost == 0:
                    margin_percent = prod_categ.margin_percent * product.standard_price / 100
                    product.final_sale_price = product.standard_price + margin_percent
                    product.final_sale_price = self.roundup_amount(int(product.standard_price))
                    product.price_status = 'updated'
                else:        
                    margin_percent = prod_categ.margin_percent * product.new_cost / 100
                    product.final_sale_price = product.new_cost + margin_percent
                    product.final_sale_price = self.roundup_amount(int(product.final_sale_price))
                    product.price_status = 'updated'
        return {'type': 'ir.actions.act_window_close'}

    