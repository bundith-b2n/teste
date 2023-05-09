from odoo import http, fields, exceptions, _
from odoo.http import Controller, Response, request, route
import requests
from urllib.request import urlopen
# from pyzbar.pyzbar import decode
from PIL import Image
import base64
import json

class WebsiteNotice(http.Controller):
    url = 'https://member.kokkoksole.com/'
    headers = {'Content-Type': 'application/json'}

    @http.route('/api/notice', csrf=False, type='http', auth="public", methods=['GET'], website=True)
    def post_notice(self, phone, title, body):
        # access_key = request.httprequest.headers.get("access_token")
        notice_url = 'api/v1/third-party/odoo/push-notification'
        vals = {
            "phone": phone,
            "title": title,
            "body": body,
        }
        data = json.dumps(vals)
        
        response = requests.request("POST", self.url + notice_url, data=data, headers=self.headers) 
        status = json.loads(response.text)

        if status.get('status') == True:
            return response.text
        else:
            data = json.dumps({
                'message': 'Not Success',
                'status': False,
            })
            headers = []
            return request.make_response(data, headers)

    # @http.route('/api/register_member', type='json', auth="none", methods=['POST'], website=True)
    # def post_register_member(self):
    #     register_url = 'api/v2/member/register'
    #     data = request.httprequest.data.decode('utf-8')
    #     data = json.loads(data)
    #     # print('======data=====>>>',data)

    #     response = requests.request("POST", self.url + register_url, data=json.dumps(data), headers=self.headers) 
    #     status = json.loads(response.text)
    #     # print('======status=====>>>',status)

    #     if status.get('status') == True:
    #         return response.text
    #     else:
    #         return {
    #             'message': 'Not Success',
    #             'status': False,
    #         }