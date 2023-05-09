# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import json
import requests
from odoo.http import Response, request
from datetime import datetime, timedelta

class WalletRecharge(models.TransientModel):
    _inherit = 'wallet.recharge'

    def post(self):
        res = super(WalletRecharge, self).post()
        active_id = self.env.context.get('active_id')
        partner_id = self.env['res.partner'].browse(active_id)
        # print('===partner_id===>>>',partner_id)
        url = self.env.company.get_base_url() + '/api/notice?phone=%s&title=%s&body=%s' % (
                                                partner_id.phone,
                                                'Wallet Recharge',
                                                'Your Recharge: ' + "{:,.2f}".format(self.recharge_amount) + '\nYour Balance: ' + "{:,.2f}".format(partner_id.wallet_balance) 
                                            )
        
        headers = {}
        data = {}

        response = requests.request("GET", url, headers=headers, data=data)

        notice = self.env['res.partner.notice'].sudo().create({
            'partner_id': partner_id.id,
            'name': 'Wallet Recharge',
            'date': datetime.now(),
            'body': 'Your Recharge: ' + "{:,.2f}".format(self.recharge_amount) + '\nYour Balance: ' + "{:,.2f}".format(partner_id.wallet_balance),
        })
        return res