from odoo import models, fields, api

class PurchaseRequest(models.Model):
     _inherit = 'purchase.request'

     confirm_id = fields.Many2one('res.users', string='Confirm by')