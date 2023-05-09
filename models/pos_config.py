# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class pos_config(models.Model):
    _inherit = 'pos.config'

    wallet_account = fields.Many2one('account.account', string='Wallet Account')

# class POS_Order(models.Model):
#     _inherit = 'pos.order'

#     phone_kkp = fields.Char('Phone Number KKP')
#     payment_kkp_status = fields.Selection([
#         ('no have', 'No have'),
#         ('no_receive', 'No Receive'),
#         ('received', 'Received'),
#     ], string='Payment KKP Status')