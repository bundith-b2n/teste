from odoo import http, fields, exceptions, _
from odoo.http import Controller, Response, request, route
import requests
from urllib.request import urlopen
# from pyzbar.pyzbar import decode
from PIL import Image
import base64
import json

class WebsiteNotice(http.Controller):
    url = 'https://member.kokkoksole.com/api/v1/third-party/odoo/push-notification'
    headers = {'Content-Type': 'application/json'}

    @http.route('/api/notice', csrf=False, type='http', auth="public", methods=['GET'], website=True)
    def post_notice(self, phone, title, body):
        # access_key = request.httprequest.headers.get("access_token")
        vals = {
            "phone": phone,
            "title": title,
            "body": body,
        }
        data = json.dumps(vals)
        
        response = requests.request("POST", self.url, data=data, headers=self.headers) 
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