# -*- coding: utf-8 -*-
from email.policy import default
from odoo import api, fields, models, _
from datetime import datetime
import math
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_round

class ProductBatchPriceWizard(models.TransientModel):
    _name = "product.batch.price.wizard"
    _description = "Product Batch Price Wizard"
    
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

    picking_ids = fields.Many2many('stock.picking', domain=[('picking_type_code','=','incoming'),('state','=','done')], string="Stock Picking")
    # country_import_ids = fields.Many2many('lod.country.import', string="Country Import")
    landed_cost_ids = fields.One2many('product.landed.cost.line.wizard', 'product_price_id', string='Product Landed Cost')
    total_landed_amount = fields.Float('Total Landed Amount', compute='_compute_total_amount')
    landed_cost_type = fields.Selection([
        ('percent', 'Average Percent'),
        ('amount', 'Average Amount'),
    ], default='percent', string='Landed Cost Type')

    @api.depends('landed_cost_ids','landed_cost_ids.price_unit')
    def _compute_total_amount(self):
        for rec in self:
            total = 0
            for landed in rec.landed_cost_ids:
                total += landed.price_unit

            rec.total_landed_amount = total

    def action_confirm__(self):
        for picking in self.picking_ids:
            po_id = self.env['purchase.order'].search([('name','=',picking.origin)])
            rate = 1
            if po_id.currency_id.id != self.env.company.currency_id.id:
                rate_obj = self.env['res.currency.rate']
                rate = rate_obj.search([('currency_id', '=', po_id.currency_id.id), ('name', '=', fields.Date.to_string(po_id.date_order)),
                            ('company_id', '=', self.env.company.id)])
                rate = rate.inverse_company_rate
                if rate == 0:
                    rate = rate_obj.search([('currency_id', '=', po_id.currency_id.id), ('name', '<', fields.Date.to_string(po_id.date_order)),
                            ('company_id', '=', self.env.company.id)], limit=1)
                    rate = rate.inverse_company_rate
            for po_line in po_id.order_line:
                if po_line.display_type == False:
                    print('====po_line====>',po_line.product_id.name,', ',po_line.product_id.categ_id.name)
                    product = po_line.product_id
                    cost_order_unit = (po_line.price_subtotal * rate) / (po_line.product_qty * product.unit)
                    quantity_order_unit = po_line.product_qty * product.unit
                    for child_u in product.product_relation_id.child_relation_ids:
                        if child_u != False:
                            if (quantity_order_unit == 0):
                                quantity_order_unit = 1
                            else:
                                quantity_order_unit = quantity_order_unit 
                        # print('===quantity_order_unit===>',quantity_order_unit)
                        # print('===cost_order_unit===>',cost_order_unit)
                        # print('===child_u.unit===>',child_u.unit)
                        # print('===rate===>',rate)
                            new_cost = ((quantity_order_unit * cost_order_unit) / quantity_order_unit) * child_u.unit
                            # print('===new_cost===>',new_cost)
                            child_u.write({
                                'standard_price': new_cost
                                })
            picking.is_calculated = True

    def action_confirm(self):
        po_amount = amount = 0
        for pick in self.picking_ids:
            rate = 1
            po_id = self.env['purchase.order'].search([('name','=',pick.origin)])
            if po_id.currency_id.id != self.env.company.currency_id.id:
                rate_obj = self.env['res.currency.rate']
                rate = rate_obj.search([('currency_id', '=', po_id.currency_id.id), ('name', '=', fields.Date.to_string(po_id.date_order)),
                            ('company_id', '=', self.env.company.id)])
                rate = rate.inverse_company_rate
                if rate == 0.0:
                    rate = rate_obj.search([('currency_id', '=', po_id.currency_id.id), ('name', '<', fields.Date.to_string(po_id.date_order)),
                            ('company_id', '=', self.env.company.id)], limit=1)
                    rate = rate.inverse_company_rate
            else:
                rate = 1.00

            amount = po_id.amount_total * rate
            po_amount += amount 
        
        for picking in self.picking_ids:
            po_rate = 1
            pick_po_id = self.env['purchase.order'].search([('name','=',picking.origin)])
            if pick_po_id.currency_id.id != self.env.company.currency_id.id:
                rate_obj = self.env['res.currency.rate']
                po_rate = rate_obj.search([('currency_id', '=', pick_po_id.currency_id.id), ('name', '=', fields.Date.to_string(pick_po_id.date_order)),
                            ('company_id', '=', self.env.company.id)])
                po_rate = po_rate.inverse_company_rate
                if po_rate == 0.0:
                    po_rate = rate_obj.search([('currency_id', '=', pick_po_id.currency_id.id), ('name', '<', fields.Date.to_string(pick_po_id.date_order)),
                            ('company_id', '=', self.env.company.id)], limit=1)
                    po_rate = po_rate.inverse_company_rate
            else:
                po_rate = 1.00

            sum_qty_done = 0
            for sum_qty in picking.move_ids_without_package:
                sum_qty_done += sum_qty.product_id.unit * sum_qty.quantity_done

            avg_landed_cost = self.total_landed_amount / sum_qty_done
            for line in picking.move_ids_without_package:
                for po_line in pick_po_id.order_line:
                    if line.product_id.id == po_line.product_id.id and po_line.display_type == False:
                        product = line.product_id
                        current_quantity_unit = 0
                        quantity_order_unit = 0
                        
                        current_cost_unit = product.product_relation_id.standard_price
                        quantity_order_unit = line.quantity_done * product.unit
                        quantity_order_pack = line.quantity_done * product.unit_pack

                        if (product.unit == 0):
                            product.unit = product.unit = 1
                        else: product.unit = product.unit
                        
                        cost_order_unit = (po_line.price_subtotal * po_rate) / (po_line.product_qty * product.unit)
                        
                        
                        # vendor_list = []
                        # for child in product.product_relation_id.child_relation_ids:
                        #     current_quantity_unit += child.quantity_unit
                        #     for seller in child.seller_ids:
                        #         if seller.id:
                        #             val = {
                        #                 'name': seller.name.id,
                        #                 'product_tmpl_id': 0,
                        #                 'min_qty': 0,
                        #                 'price': 0,
                        #                 'currency_id': 95,
                        #             }
                        #             vendor_list.append(val)
                        

                        # current_quantity_unit = abs(current_quantity_unit - quantity_order_unit) 

                        discount_percent = po_line.discount
                        discount_amount = po_line.discount_amount / po_line.product_qty / po_line.unit
                        
                        for child_u in product.product_relation_id.child_relation_ids:
                            if child_u != False:
                                # if (current_quantity_unit + quantity_order_unit) * child_u.unit == 0:
                                #     raise UserError(_("product(current_quantity_unit): " + child_u.name + '/' + str(current_quantity_unit) + '/' + str(quantity_order_unit) + '/' + str(child_u.unit)))
                                # if child_u.unit == 0:
                                #     raise UserError(_("product(child_u.unit): " + child_u.name))

                                avg_cost = 0
                                if self.landed_cost_type == 'amount':
                                    if child_u.uom_id.name =='Box':
                                        avg_cost = avg_landed_cost * child_u.unit
                                    elif child_u.uom_id.name == 'Pack':
                                        if (quantity_order_pack == 0):
                                            quantity_order_pack = 1
                                        else:
                                            quantity_order_pack = quantity_order_pack
                                        avg_cost = avg_landed_cost * child_u.unit
                                    else:
                                        if (quantity_order_unit == 0):
                                            quantity_order_unit = 1
                                        else:
                                            quantity_order_unit = quantity_order_unit                                    
                                        avg_cost = avg_landed_cost
                                else:
                                    avg_cost = (self.total_landed_amount * 100) / po_amount
                                    if child_u.uom_id.name == 'Pack':
                                        if (quantity_order_pack == 0):
                                            quantity_order_pack = 1
                                        else:
                                            quantity_order_pack = quantity_order_pack
                                    else:
                                        if (quantity_order_unit ==0):
                                            quantity_order_unit = 1
                                        else:
                                            quantity_order_unit = quantity_order_unit      
                                # new_cost = (((current_quantity_unit * current_cost_unit) + (quantity_order_unit * cost_order_unit)) / (current_quantity_unit + quantity_order_unit)) * child_u.unit
                                ### ແລ່ນ ຄັ້ງທໍາອິດໃຫ້ ປັບ ຈໍານວນໃນສາງ ແລະ ຕົ້ນທຶນເປັນ 0 ໂດຍບໍ່ຈໍາເປັນ ຕ້ອງລ້າງຖານຂໍ້ມູນ 
                                new_cost = ((quantity_order_unit * cost_order_unit) / quantity_order_unit) * child_u.unit

                                
                                if self.landed_cost_type == 'amount':
                                    child_u.write({
                                        'new_cost': new_cost + avg_cost,
                                        'price_status': 'checked'
                                        })
                                else:
                                    avg_cost = (avg_cost * new_cost / 100)
                                    child_u.write({
                                        'new_cost': new_cost + avg_cost,
                                        'price_status': 'checked'
                                        })
                                margin_ids = child_u.country_import_id.margin_ids

                                # if child_u.seller_ids.ids == []:
                                #     if vendor_list != []: 
                                #         vendor_list[0]['product_tmpl_id'] = child_u.id
                                #         vendor_list[0]['price'] = child_u.standard_price
                                #         # print('===vendor_list==>',vendor_list)
                                #         self.env['product.supplierinfo'].create(vendor_list)

                                # his_list = []
                                his_values = {
                                    'product_template_id': child_u.id,
                                    'po_id': pick_po_id.id,
                                    'rate': po_rate,
                                    'current_cost': child_u.standard_price,
                                    'order_cost': new_cost + discount_amount * child_u.unit * po_rate,
                                    'dis_percent': discount_percent,
                                    'dis_amount': discount_amount * child_u.unit * po_rate,
                                    'new_cost': new_cost,
                                    'landed_percent': float_round(avg_cost, 2),
                                    'landed_amount': avg_cost,
                                    'final_new_cost': new_cost + avg_cost,
                                }
                                self.env['lod.landed.cost.history'].create(his_values)

                                for margin in margin_ids:
                                    if margin.uom_id.id == child_u.uom_id.id:
                                        child_u.margin_percent = margin.margin_percent
                                        child_u.margin_amount = child_u.new_cost + (child_u.new_cost * (margin.margin_percent/100))
                                        child_u.markup_percent = margin.markup_percent
                                        child_u.markup_amount = child_u.margin_amount + (child_u.new_cost * (margin.markup_percent/100))
                                        child_u.final_sale_price = self.roundup_amount(int(child_u.markup_amount))
                                        
            picking.is_calculated = True           
                        
        return {'type': 'ir.actions.act_window_close'}


    
class ProductLandedCodeLineWizard(models.TransientModel):
    _name = "product.landed.cost.line.wizard"
    _description = "Product Landed Cost Wizard"

    product_price_id = fields.Many2one('product.batch.price.wizard', string='Product Price')
    name = fields.Char('Description')
    product_id = fields.Many2one('product.template', domain=[('landed_cost_ok','=',True),('detailed_type','=','service')], string='Product')
    account_id = fields.Many2one('account.account', string='Account')
    price_unit  = fields.Float('Price')