from odoo import http, fields, exceptions, _
from odoo.http import Controller, Response, request, route
from datetime import date, datetime, time, timedelta
import requests
from urllib.request import urlopen
# from pyzbar.pyzbar import decode
from PIL import Image
import base64
import json

# class API_Accounting_Odoo_to_HQ_(http.Controller):
#         # url = 'https://member.kokkoksole.com/api/v1/third-party/odoo/push-notification'
#         # headers = {'Content-Type': 'application/json'}

#     @http.route('/api/notice', csrf=False, type='http', auth="public", methods=['GET'], website=True)
#     def post_notice(self, phone, title, body):
#         vals = {
#             "phone": phone,
#             "title": title,
#             "body": body,
#         }
#         data = json.dumps(vals)
        
#         response = requests.request("POST", self.url, data=data, headers=self.headers) 
#         status = json.loads(response.text)

#         if status.get('status') == True:
#             return response.text
#         else:
#             data = json.dumps({
#                 'message': 'Not Success',
#                 'status': False,
#             })
#             headers = []
#             return request.make_response(data, headers)
        

class Accounting_HQ_API(http.Controller):

    def _check_access(self, context):
        header = request.env['rest.api'].sudo().search([])
        user_id = request.env['res.users'].sudo().search([('name','=',context.get('user_name'))])
        key_list = []
        for key in header:
            key_list.append(key.api_key)
        if context.get('api_key') in key_list:
            if user_id:
                return {
                        'user_name': user_id.name,
                        'status': True
                        }
            else:
                return {
                    'user_name': False,
                    'status': False,
                }
        else:
            return {'status': False}
        

    @http.route('/api/accounting_hq', type='json', auth="none", methods=['POST'], website=True)
    def accounting_hq(self):
        headers = request.httprequest.headers
        user_login = headers.get('user_login')
        password = headers.get('password')
        password = base64.b64decode(password)
        database = headers.get('database')
        login = request.session.authenticate(database, user_login, password)
        session_info = request.env['ir.http'].session_info()

        data = request.httprequest.data.decode('utf-8')
        data = json.loads(data)
        access_key = self._check_access(headers)
        if access_key.get('user_name') == False:
            return {
                'message': 'Not Success, user_id invalid',
                'status': False,
            }
        
        if access_key.get('status') == True:
            account_move_id = request.env['account.move'].sudo().search([('name','=',data.get('invoice_no'))])
            # if account_move_id.move_type == 'in_invoice':
            if not account_move_id or account_move_id.payment_state not in ['not_paid','in_payment']:
                return {
                    'message': 'Not Success. Please check reference no '+str(data.get('invoice_no')),
                    'status': False,
                }
            if account_move_id.state == 'draft':
                return {
                    'message': 'Not Success. Please posted journal entry number'+str(data.get('invoice_no')),
                    'status': False,
                }
            register_payment = account_move_id.action_register_payment()
            context = register_payment['context']

            wizard_payment = request.env['account.payment.register'].sudo().with_context(active_model=context.get('active_model'), active_ids=context.get('active_ids')).create({
                'amount': data.get('amount'),
                'journal_id': data.get('journal_id'),
                'currency_id': data.get('currency_id'),
                'payment_date': data.get('date')
            })

            wizard_payment._create_payments()
            
            request.session.logout()
            return {
                'message': 'Success',
                'status': True,
            }
        else:
            return {
                'message': 'Not Success, access_key invalid',
                'status': False,
            }