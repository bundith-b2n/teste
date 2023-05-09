# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class ProductCategory(models.Model):
    _inherit = "product.category"
    _order = "code"  

    name = fields.Char('Name', index=True, required=True, translate=True)
    code = fields.Char('Code')
    categ_public_id = fields.Many2one('product.public.category', string='e-Commerce Category')
    company_id = fields.Many2one('res.company', string='Company')
    categ_level = fields.Selection([('level_1','Level 1'),('level_2','Level 2'),('level_3','Level 3'),('level_3','Level 3'),('level_4','Level 4'),('level_5','Level 5')], default='level_1',)
    
class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'
    _order = 'code_public_cate, sequence, name, id'

    code_public_cate = fields.Char(string='Code')

class ProductPosCategory(models.Model):
    _inherit = 'pos.category'
    _order = 'code_pos_cate, sequence, name'

    code_pos_cate = fields.Char(string='Code')



class ProductProduct(models.Model):
    _inherit = "product.product"

    def generate_barcode(self):
        for rec in self:
            if rec.barcode == False:
                rec.barcode = '85' + '{:0>11}'.format(rec.id)

class ProductTemplate(models.Model):
    _inherit = 'product.template'
