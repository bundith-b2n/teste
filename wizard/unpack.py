# -*- coding: utf-8 -*-
from email.policy import default
from odoo import api, fields, models, _


class UnpackProductWizard(models.TransientModel):
    _name = "unpack.wizard"
    _description = "Unpack"

    @api.model
    def default_get_product(self):
        active_id = self.env.context.get("active_id")
        product = self.env['product.template'].browse(active_id)
        return product.id
    
    @api.model
    def _default_get_products(self):
        active_id = self.env.context.get("active_id")
        product = self.env['product.template'].browse(active_id)
        default = product.product_relation_id.child_relation_ids.ids
        return default
    
    @api.model
    def _default_get_picking_type(self):
        stock_picking_type = self.env['stock.picking.type'].search([('code','=','mrp_operation')],limit=1)
        return stock_picking_type.id
    
    product_id = fields.Many2one('product.template', string="Product", default=default_get_product, readonly=True, store=True)
    product_ids = fields.Many2many('product.template', string="Products", default=_default_get_products)
    product_qty = fields.Float(compute='_compute_qty', string="Product Qty")
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='UOM')
    scheduled_date = fields.Datetime('Scheduled Date', default=fields.Datetime.now())
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, string='Responsible', readonly=True, store=True)
    unpack_line_ids = fields.One2many('unpack.line.wizard', 'unpack_id', string='Unpack Line')
    picking_type_id = fields.Many2one('stock.picking.type', default=_default_get_picking_type, domain=[('code','=','mrp_operation')], string='Operation Type')
    location_src_id = fields.Many2one('stock.location', string='Source Location')
    location_dest_id = fields.Many2one('stock.location', string='Destination Location')
    source_document = fields.Char(string='Source Document')
    
    @api.depends('unpack_line_ids.product_qty')
    def _compute_qty(self):
        for rec in self:
            quantity = 0.0
            for line in rec.unpack_line_ids:
                quantity += line.product_qty * line.product_id.unit

            rec.product_qty = quantity
            
    def unpack_confirm(self):
        move_raw_list = []
        stock_loc = self.env['stock.location'].search([('usage','=','production')], limit=1)
        for line in self.unpack_line_ids:
            move_raw = {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'location_id': line.location_id.id,
                'location_dest_id': stock_loc.id,
                'product_uom_qty': line.product_qty,
                'price_unit': 0,
                'product_uom': line.uom_id.id,
                'warehouse_id': self.picking_type_id.warehouse_id.id,
                'propagate_cancel': True,
            }
            move_raw_list.append((0, 0, move_raw))
        
        values = {
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'product_uom_id': self.uom_id.id,
            'qty_producing': 0.0,
            'date_planned_start': self.scheduled_date,
            'user_id': self.user_id.id,
            'picking_type_id': self.picking_type_id.id,
            'location_src_id': self.location_src_id.id,
            'location_dest_id': self.location_dest_id.id,
            'move_raw_ids': move_raw_list,
        }
    
        Manufac = self.env['mrp.production'].create(values)
        
        move_raw = []
        stock_loc = self.env['stock.location'].search([('usage','=','production')], limit=1)
        stock_move_new = self.env['stock.move']
        for line in self.unpack_line_ids:
            moves_new = {
                'product_id': self.product_id.id,
                'name': 'New',
                'location_id': stock_loc.id,
                'location_dest_id': line.location_id.id,
                'product_uom_qty': self.product_qty,
                'product_uom': self.uom_id.id,
                'origin': Manufac.name,
                'reference': Manufac.name,
                'group_id': Manufac.move_raw_ids[0].group_id.id,
                'procure_method': 'make_to_stock',
                'picking_type_id': self.picking_type_id.id,
                'propagate_cancel': False,
                'production_id': Manufac.move_raw_ids[0].raw_material_production_id.id,
                'warehouse_id': self.picking_type_id.warehouse_id.id,
            }
            stock_move_new.create(moves_new)
            
        return {'type': 'ir.actions.act_window_close'}
    
    @api.model
    def default_get(self, fields):
        vals = super(UnpackProductWizard, self).default_get(fields)
        if 'picking_type_id' in fields:
            picking_type = self.env['stock.picking.type'].browse(int(vals.get('picking_type_id')))
            vals['location_src_id'] = picking_type.default_location_src_id.id
            vals['location_dest_id'] = picking_type.default_location_dest_id.id
        return vals
    
class UnpackProductLineWizard(models.TransientModel):
    _name = "unpack.line.wizard"
    _description = "Unpack Line"

    unpack_id = fields.Many2one('unpack.wizard', string="Unpack Product")
    product_id = fields.Many2one('product.template', string="Product")
    location_id = fields.Many2one('stock.location', related='unpack_id.location_src_id', string="Location")
    product_qty = fields.Float(string="Quantity")
    uom_id = fields.Many2one('uom.uom', related='product_id.uom_id', string='UOM')
