# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, RedirectWarning

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(selection_add=[
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),                   
        ('purchase_approval', 'To Purchase Approval'),  # New status
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)
    approval_id = fields.Many2one('res.users', string='Approver')
    confirm_id = fields.Many2one('res.users', string='Confirm by')
    

    def button_approval(self):
        for order in self:
            order.state = 'purchase_approval'
        return self.write({"approval_id": self.env.uid})
        # return True

    def button_confirm(self):
        for order in self:
            if order.state not in ['purchase_approval']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        # return True
        return self.write({"confirm_id": self.env.uid})

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    transport_fee = fields.Float('Transport Fee')