import itertools
import logging
from collections import defaultdict
import string
import math

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import ValidationError, RedirectWarning, UserError
from odoo.osv import expression
from check_digit_EAN13.check_digit import get_check_digit

class ProductTemplate(models.Model):
    _inherit = "product.template"

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

    model_field = fields.Char('Model ID', copy=False,)
    _sql_constraints = [('model_field', 'unique (model_field)', "The Model ID must be unique, this one is already assigned to another (model_field).")]
    # plu = fields.Char('PLU Scale', copy=False,)
    # _sql_constraints = [('plu', 'unique (plu)', "The Model ID must be unique, this one is already assigned to another (plu).")]
    serial_no  = fields.Char('Serial Number', copy=False)
    _sql_constraints = [('serial_no', 'unique (serial_no)',"The Model ID must be unique, this one is already assigned to another (serial_no).")]
    country_id = fields.Many2one('res.country', string="Country")
    country_import_id = fields.Many2one('lod.country.import', string="Country Import")
    partner_id = fields.Many2one('res.partner', string="Partner")
    is_product_discount = fields.Boolean('Discount')
    new_cost = fields.Float('New Cost', digits=(16, 2))
    margin_percent = fields.Float('Margin %', digits=(16, 2))
    margin_amount = fields.Float('Margin Amt', digits=(16, 2))
    markup_percent = fields.Float('Markup %', digits=(16, 2))
    markup_amount = fields.Float('Markup Amt', digits=(16, 2))
    old_sale_price = fields.Float('Old Sale Price', digits=(16, 2))
    final_sale_price = fields.Float('Final Sale Price', digits=(16, 2))
    competitor_cost_1 = fields.Float('Competitor 1')
    competitor_perc_1 = fields.Float('Comp1(%)')
    competitor_cost_2 = fields.Float('Competitor 2')
    competitor_perc_2 = fields.Float('Comp2(%)')
    competitor_cost_3 = fields.Float('Competitor 3')
    competitor_perc_3 = fields.Float('Comp3(%)')
    competitor_cost_4 = fields.Float('Competitor 4')
    competitor_perc_4 = fields.Float('Comp4(%)')
    competitor_cost_5 = fields.Float('Competitor 5')
    competitor_perc_5 = fields.Float('Comp5(%)')
    last_update = fields.Datetime('Updated')
    last_approved = fields.Datetime('Approved')
    price_status = fields.Selection([('pending', 'Pending'),
                                    ('approved', 'Approved'),
                                    ('updated', 'Updated'),
                                    ('checked', 'Checked'),
                                    ], string='Status',
                                    default='pending')

    dif_sale_price = fields.Float('Dif', compute='_compute_dif_sale_price')
    dif_sale_percent = fields.Float('Dif %', compute='_compute_dif_sale_price')
    diff_cost_sale = fields.Float('Diff', compute='_compute_dif_sale_price')
    
    landed_cost_history_ids = fields.One2many('lod.landed.cost.history', 'product_template_id', string='Landed Cost History')

    @api.depends('new_cost', 'final_sale_price', 'list_price')
    def _compute_dif_sale_price(self):
        for rec in self:
            rec.dif_sale_price = rec.list_price - rec.final_sale_price
            if rec.final_sale_price == 0:
                rec.dif_sale_percent = 0
            else:
                rec.dif_sale_percent = -1 * (rec.dif_sale_price * 100 / rec.final_sale_price)
            rec.diff_cost_sale = rec.list_price - rec.standard_price
            # if rec.diff_cost_sale < 0:
            #     if rec.uom_id.name == "Unit":
            #         rec.list_price = ((rec.standard_price * 5)/100) + rec.standard_price
            #     elif rec.uom_id.name == "Pack":
            #         rec.list_price = ((rec.standard_price * 4)/100) + rec.standard_price
            #     elif rec.uom_id.name == "Box":
            #         rec.list_price = ((rec.standard_price * 3)/100) + rec.standard_price

    def action_update_sale_price(self):
        for rec in self:
            rec.old_sale_price = rec.list_price
            rec.list_price = self.roundup_amount(int(rec.final_sale_price))
            rec.last_update = fields.Datetime.now()
            rec.price_status = 'updated'

    def action_update_new_cost(self):
        for rec in self:
            rec.standard_price = self.roundup_amount(int(rec.new_cost))
    
    def action_approve_sale_price(self):
        for rec in self:
            rec.last_approved = fields.Datetime.now()
            rec.price_status = 'approved'

    def action_update_competitor_price(self):
        for rec in self:
            competitor_id = self.env['x_tmp_competitor'].search([('x_name','=',rec.barcode)])
            for comp in competitor_id:
                rec.competitor_cost_1 = comp.x_competitor_1
                rec.competitor_cost_2 = comp.x_competitor_2
                rec.competitor_cost_3 = comp.x_competitor_3
                rec.competitor_cost_4 = comp.x_competitor_4
                rec.competitor_cost_5 = comp.x_competitor_5

    # def action_generate_code_sku(self):
    #     for rec in self:
    #         if rec.is_main_product_relate:
    #             sequence = self.env['ir.sequence'].next_by_code('product.sku.sequence')
    #             print('===sequence==>>',sequence)
    #             for child in rec.child_relation_ids:
    #                 if child.to_weight == False:
    #                     child.default_code = sequence

    def action_generate_code_sku(self):
        for rec in self:
            vendor_list = []
            for child in rec.child_relation_ids:
                for seller in child.seller_ids:
                    if seller.id:
                        val = {
                            'name': seller.name.id,
                            'product_tmpl_id': 0,
                            'min_qty': 0,
                            'price': 0,
                            'currency_id': 95,
                        }
                        vendor_list.append(val)
            if rec.seller_ids.ids == [] and vendor_list != []:
                vendor_list[0]['product_tmpl_id'] = rec.id
                vendor_list[0]['price'] = rec.standard_price
                # print('===vendor_list==>',vendor_list)
                self.env['product.supplierinfo'].create(vendor_list)

            if rec.is_main_product_relate:
                sequence = self.env['ir.sequence'].next_by_code('product.sku.sequence')
                for child in rec.child_relation_ids:
                    if child.to_weight == False:
                        child.default_code = sequence
                        child.country_import_id = rec.country_import_id.id

            
    @api.onchange('categ_id')
    def onchange_categ_id(self):
        if self.categ_id.categ_public_id:
            self.update({'public_categ_ids':[self.categ_id.categ_public_id.id]})
        else:
            self.update({'public_categ_ids': False})

    @api.onchange('barcode')
    def _onchange_barcode(self):
        barcode = self.barcode
        if barcode != False:
            if len(barcode) == 12 and barcode[:2] == '21':
                actual_barcode = get_check_digit(barcode)
                self.barcode = actual_barcode
   
    @api.model
    def create(self, values):
        if 'barcode' in values:
            barcode = values['barcode']
            if barcode != False:
                if len(barcode) == 12 and barcode[:2] == '21':
                    actual_barcode = get_check_digit(barcode)
                    values['barcode'] = actual_barcode
        res = super(ProductTemplate, self).create(values)
        return res

    def generate_barcode(self):
        for rec in self:
            if rec.barcode == False:
                rec.barcode = '85' + '{:0>11}'.format(rec.id)


class CountryImport(models.Model):
    _name = "lod.country.import"
    _description = "Country Import"

    name = fields.Char('Name', required=True)
    margin_ids = fields.Many2many('lod.margin.config', string='Margin')


class MarginConfiguration(models.Model):
    _name = "lod.margin.config"
    _description = "Margin Configuration"

    name = fields.Char('Name', required=True)
    uom_id = fields.Many2one('uom.uom', string='UOM')
    margin_percent = fields.Float('Margin Percent')
    markup_percent = fields.Float('Markup Percent', digits=(16, 2), compute='_compute_margin_percent')
    
    @api.depends('margin_percent')
    def _compute_margin_percent(self):
        for rec in self:
            rec.markup_percent = ((rec.margin_percent/100) / (1 - (rec.margin_percent/100)))*100

class LandedCostHistory(models.Model):
    _name = "lod.landed.cost.history"
    _description = "Landed Cost History"

    product_template_id = fields.Many2one('product.template', string='Product Template')
    name = fields.Char('Name')
    po_id = fields.Many2one('purchase.order', string='Purchase Order')
    date = fields.Datetime('Date', related='po_id.date_order')
    rate = fields.Float('Rate')
    currency = fields.Char('Currency', related='po_id.currency_id.name')
    landed_percent = fields.Float('Landed Percent')
    landed_amount = fields.Float('Landed Amount')
    dis_percent = fields.Float('DISC Percent')
    dis_amount = fields.Float('DISC Amount')
    current_cost = fields.Float('Current Cost')
    order_cost = fields.Float('Order Cost')
    new_cost = fields.Float('New Cost')
    final_new_cost = fields.Float('Final New Cost')
