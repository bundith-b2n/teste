# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    def check_main_wallet_balance_menu(self):
        return True

    def check_batch_wallet_balance_menu(self):
        return True
    

 