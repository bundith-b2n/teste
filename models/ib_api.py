# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import base64
import qrcode
import io
import json
import hashlib
import random
import requests
from odoo.exceptions import UserError, RedirectWarning


class IBTransaction(models.Model):
    _name = 'lod.ib.transaction'
    _description = 'Get Transaction ID'

    name = fields.Char('Transaction No')
    date = fields.Datetime('Date')
    receive_order_no = fields.Char('Receive Order No')
    amount = fields.Float('Amount')
    phone = fields.Char('Phone')
    # branch_id = fields.Many2one('res.branch', string='Branch')
    # pos_id = fields.Many2one('pos.config', string='POS')
    branch_id = fields.Char('Branch')
    pos_id = fields.Char('POS')

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_main_wallet = fields.Boolean('Is Main Wallet')
    is_branch_wallet = fields.Boolean('Is Branch Wallet')
    wallet_name = fields.Char('Wallet Name')
    wallet_mobile = fields.Char('Wallet Mobile Number')
    merchant_id = fields.Char('Merchant ID')

class IBTransferMoney(models.Model):
    _inherit = 'account.payment'

    def get_api_wallet_cash_out(self):
        kok_kok_url = self.env['ir.config_parameter'].sudo().get_param('pos_kok_payment_cr.kok_kok_url')
        member_id = self.env['ir.config_parameter'].sudo().get_param('pos_kok_payment_cr.member_id')
        memberToken = self.env['ir.config_parameter'].sudo().get_param('pos_kok_payment_cr.login_token')

        cash_in_url = kok_kok_url+"/member-api-service/v1.0.1/wallet/register/transaction"
        # memberToken = data['responseObj'].get('memberToken')
        headers = {'Content-Type': 'application/json', 'AUTH_TOKEN': memberToken}
        tran_data = {
            "memberId": member_id,
            "txnType": "CSHOUT",
            "memberRef": self.name + '/' + self.ref,
            "txnAmount": self.amount,
            "txnCurrency": "418",
            # "fromCustName": self.journal_id.wallet_name,
            "fromMobile": self.journal_id.wallet_mobile,
            # "toMobile": self.destination_journal_id.wallet_mobile,
            "remarks": "cash in member from " + str(self.journal_id.wallet_mobile),
        }
        response = requests.post(cash_in_url, data=json.dumps(tran_data), headers=headers)
        response_data = response.json()
        # print("\n ___response_data_______", response_data)
        # response_data = {}
        if response_data.get('respStatus') == 'SUCCESS':
            cash_confirm_in_url = kok_kok_url+"/member-api-service/v1.0.1/wallet/confirm/transaction"
            headers = {'Content-Type': 'application/json', 'AUTH_TOKEN': memberToken}

            data_confirm = {
                "memberId": member_id,
                "txnType": "CSHOUT",
                "tokenId": response_data.get('responseObj').get('tokenId'),
                "memberRef": self.name + '/' + self.ref,
                "txnAmount": self.amount,
                "txnCurrency": "418",
                # "fromCustName": self.journal_id.wallet_name,
                "fromMobile": self.journal_id.wallet_mobile,
                # "toMobile": self.destination_journal_id.wallet_mobile,
                "remarks": "cash in member to " + str(self.journal_id.wallet_mobile),
            }
            response_cf = requests.post(cash_confirm_in_url, data=json.dumps(data_confirm), headers=headers)
            cf_response = response_cf.json()
            # print("\n ___Confirm__response_______", cf_response)
            if cf_response.get('respStatus') == 'SUCCESS':
                pass
            else:
                raise UserError(_('You can not confirm transfer'))
        else:
            raise UserError(_('You can not register transfer'))
    
        return True
        
    def action_post(self):
        res = super(IBTransferMoney, self).action_post()
        if self.is_internal_transfer == True and \
           self.journal_id.is_branch_wallet == True and \
           self.destination_journal_id.is_main_wallet == True:
            
            self.get_api_wallet_cash_out()

        return res
