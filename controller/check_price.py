from odoo import http, fields, exceptions, _
from odoo.http import Controller, Response, request, route
import requests
from urllib.request import urlopen
# from pyzbar.pyzbar import decode
from PIL import Image
import base64
import json
from odoo import http, fields, _
from odoo.http import request

class WebsiteCheckPrice(http.Controller):

    @http.route('/check_product_price', csrf=False, type='http', auth="public",  website=True)
    def check_price(self, barcode=None):
        values = {}
        if barcode != None:
            product_id = request.env['product.template'].sudo().search([('barcode','=',barcode)])
            relation_ids = []
            if len(product_id.product_relation_id.child_relation_ids.ids) >= 1:
                for rel in product_id.product_relation_id.child_relation_ids:
                    if product_id.id != rel.id:
                        relation_ids.append(rel)

            values.update({
                'relation_ids': relation_ids,
                'product_id': product_id,
            })
        return request.render("lod_kokkokm.check_price_template", values)

    @http.route('/check_product_price/post', csrf=False, type='http', auth="public", methods=['POST'], website=True)
    def check_price_post(self, barcode):
        
        return request.redirect("/check_product_price?barcode="+barcode)