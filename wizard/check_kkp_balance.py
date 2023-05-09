# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class CheckWalletBalance(models.TransientModel):
    _name = "check.wallet.balance.wizard"
    _description = "Check Wallet Balance"

    amount = fields.Float('Balance')


 