# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

# class StockWarehouse(models.Model):
#     _inherit = 'stock.warehouse'

#     is_purchase = fields.Boolean('Is Purchase')
#     is_sale = fields.Boolean('Is Sale')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    payment_date = fields.Date('Payment Date')
    currency_id = fields.Many2one('res.currency', compute='_compute_get_currency', string='Currency', store=True)
    is_calculated = fields.Boolean('Is Calculated', default=False)
    
    @api.depends('origin')
    def _compute_get_currency(self):
        for rec in self:
            if rec.origin != False:
                po_id = self.env['purchase.order'].search([('name','=',rec.origin)], limit=1)
                rec.currency_id = po_id.currency_id.id

class StockOrderpoint(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    def order_to_pr(self):
        prod_list = []
        for rec in self:
            product_line = (0, 0, {
                'product_id': rec.product_id.id,
                'name': rec.product_id.name,
                'product_qty': rec.qty_to_order,
                'product_uom_id': rec.product_id.uom_id.id,
                'unit_price': rec.product_id.standard_price,
                'date_required': fields.Datetime.now(),
                'estimated_cost': rec.product_id.standard_price,
                # 'amount_total': rec.qty_to_order * rec.product_id.standard_price,
            })
            prod_list.append(product_line)

            wh_receipt = self.env['stock.picking.type'].search([('code','=','incoming')], limit=1)


            rec.trigger = 'manual'

        product = {
            'requested_by': rec.env.user.id,
            'date_start': fields.Datetime.now(),
            'origin': rec.name,
            'picking_type_id': wh_receipt.id,
            'line_ids': prod_list,
        }
        self.env['purchase.request'].create(product)

