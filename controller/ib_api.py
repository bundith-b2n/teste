from odoo import http, fields, exceptions, _
from odoo.http import Controller, Response, request, route
from datetime import date, datetime, time, timedelta
import requests
from urllib.request import urlopen
# from pyzbar.pyzbar import decode
from PIL import Image
import base64
import json
from odoo.addons.bus.controllers.main import BusController


class Bus(BusController):
    def _poll(self, dbname, channels, last, options):
        channels = list(channels)
        if request.session.uid:
            user_id = request.env.ref('base.user_admin')
            channels.append(user_id)
        return super(Bus, self)._poll(dbname, channels, last, options)


class WebsiteNotice(http.Controller):
    # url = 'https://member.kokkoksole.com/api/v1/third-party/odoo/push-notification'
    # headers = {'Content-Type': 'application/json'}
    def _check_access(self, context):
        # return {'status': True}
        header = request.env['rest.api'].sudo().search([], limit=1)
        if header.api_key == context.get('api_key'):
            return {'status': True}
        else:
            return {'status': False}

    @http.route('/api/receipt_trans', csrf=False, type='json', auth="none", methods=['PUT'], website=True)
    def receipt_trans(self):
        data = request.httprequest.data.decode('utf-8')
        data = json.loads(data)
        access_key = self._check_access(request.httprequest.headers)
        # print("\n +++++++++++ request.httprequest.headers ++++++++++", request.httprequest.headers)
        # print("\n ++++++++++ access_key ++++++++", access_key)
        if access_key.get('status'):
            # print("\n ++++++++ data +++++", data)
            user_id = request.env.ref('base.user_admin')
            val = {
                'order_name': data.get('receive_order_no'),
                'amount': float(data.get('amount')),
                'payment_ref': data.get('transaction_no'),
                'phone': data.get('phone'),
            }
            bus_notif = [[user_id, 'pos.validate', {'type': val}]]
            request.env['bus.bus']._sendmany(bus_notif)
            request.env['lod.ib.transaction'].create({
                    'name': data.get('transaction_no'),
                    'date': fields.Datetime.now(),
                    'receive_order_no': data.get('receive_order_no'),
                    'amount': float(data.get('amount')),
                    'phone': data.get('phone'),
                    'branch_id': data.get('branch_id'),
                    'pos_id': data.get('pos_id'),
                })
            return {
                'message': 'Success',
                'status': True,
            }
        else:
            return {
                'message': 'Not Success, access_key invalid',
                'status': False,
            }
