from odoo import http, fields, exceptions, _
from odoo.http import request
from urllib.request import urlopen
# from pyzbar.pyzbar import decode
from PIL import Image
import base64
import json

class WebsiteBranch(http.Controller):

    @http.route('/request_branch', csrf=False, type='http', auth="public", methods=['GET'], website=True)
    def request_branch(self, BranchID):
        access_key = request.httprequest.headers.get("access_token")
        if access_key == 'f00357d6-24cb-4efe-b52b-6fbd525d9684':
            print('=======access_key======>>',access_key)
            branch_id = request.env['res.branch'].sudo().search([('id','=',BranchID)])
            name = str(branch_id.name)
            address = str(branch_id.address)
            vals = {
                'name': name,
                'address': address,
                'telephone': branch_id.telephone,
                'longitude': branch_id.longitude,
                'latitude': branch_id.latitude,
                'company_id': branch_id.company_id.id,
                'image': branch_id.image.decode('utf-8'),
            }
            data = json.dumps(vals)
            headers = {'Content-Type': 'application/json'}
                    
            return request.make_response(data, headers)
        else:
            data = json.dumps({
                'msg': 'Error',
                'access_key': 'access_key Not Correct',
            })
            headers = []
            return request.make_response(data, headers)