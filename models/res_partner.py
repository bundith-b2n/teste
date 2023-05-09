# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import math
import re
from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
import json
import requests
from odoo.http import Response, request
from datetime import datetime, timedelta
from odoo.exceptions import UserError, RedirectWarning


class LODResPartner(models.Model):
    _inherit = 'res.partner'
    _description =  'Customer Extend'

    url = 'https://member.kokkoksole.com/'
    headers = {'Content-Type': 'application/json'}
    
    name = fields.Char('Name', index=True, required=True, translate=True)
    partner_code = fields.Char('Customers Code')
    business_license = fields.Char('Business License')
    ref_code = fields.Char('Referent document')
    district_id = fields.Many2one('res.district', string='District')    
    is_merchant = fields.Boolean('Is Merchant')
    doc_type = fields.Selection([('family_book','Family Book'),('citicezend_id','Citizend ID'),('passport','Passport'),('vaccine_card','Vaccince Card')])
    notice_ids = fields.One2many('res.partner.notice', 'partner_id', string='Notice')
    fax = fields.Char(string='Fax')
    la_name = fields.Char(string='Name Lao')
    register_channel = fields.Selection([('mobileapp', 'Mobile App'), ('walkin', 'Walk In'), ('website', 'Website')], string='Register Channel', default='walkin',)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string='Gender')
    phone = fields.Char('phone', required=True)
    mobile = fields.Char()
    email = fields.Char()
    website = fields.Char('Website Link')
    birth_date = fields.Date(string='Birthdate', default='1999-09-09')
    
    @api.onchange('loyalty_points')
    def _onchange_loyalty_points(self):
        if self.loyalty_points != False:
            url = self.env.company.get_base_url() + '/api/notice?phone=%s&title=%s&body=%s' % (
                                                    self.phone,
                                                    'ທ່ານໄດ້ຮັບຄະແນນຈາກ KokkokM',
                                                    'ຄະແນນຂອງທ່ານມີທັງໝົດ ' + "{:,.0f}".format(self.loyalty_points)
                                                )
            
            headers = {}
            data = {}

            response = requests.request("GET", url, headers=headers, data=data)

            notice = self.env['res.partner.notice'].sudo().create({
                'partner_id': self.id,
                'name': 'Receive Point',
                'date': datetime.now(),
                'body': 'Total Point ' + "{:,.0f}".format(self.loyalty_points)
            })

    @api.onchange('district_id')
    def onchange_district_id(self):
        if self.district_id:
            if self.district_id.province_id:
                self.state_id = self.district_id.province_id
        else:
            self.state_id = ''

    
    
    @api.model
    def create(self, vals):
        member_phone = self.env['res.partner'].search([])
        phone_list = []
        for member in member_phone:
            phone_list.append(member.phone)

        res = super(LODResPartner, self).create(vals)

        if vals.get('free_member'):
            if vals.get('phone') not in phone_list:
                birth_date = ''
                if vals.get('birth_date') != False:
                    birth_date = str(vals.get('birth_date'))
                    birth_date = datetime.strptime(birth_date, "%Y-%m-%d")
                    birth_date = birth_date.strftime("%d-%m-%Y")
                image = vals.get('image_1920') or ''
                village = vals.get('city') or ''
                district = self.env['res.district'].browse(vals.get('district_id')).name or ''
                state_id = self.env['res.country.state'].browse(vals.get('state_id')).name or ''
                address = village + district + state_id

                values = {
                    "firstname" : vals.get('name') or '',
                    "lastname" : vals.get('name') or '',
                    "email" : vals.get('email') or '',
                    "phone" : vals.get('phone') or '',
                    "birth_date" : birth_date or '',
                    "address" : address,
                    "gender" : vals.get('gender').upper() if vals.get('gender') else '',
                    "image" : image,
                    "device_token" : ""
                }

                register_url = 'api/v2/member/register/odoo'
                response = requests.request("POST", self.url + register_url, data=json.dumps(values), headers=self.headers) 

            else:
              raise UserError(_('Phone number '+vals.get('phone')+' doest not exist'))
        return res
            
        

class RESDistrict(models.Model):
	_name = 'res.district'
	_description = "District"

	code = fields.Char('Code')
	name = fields.Char('Name',translate=True)
	province_id = fields.Many2one('res.country.state',string="Province")


class ResPartnerNotice(models.Model):
    _name = 'res.partner.notice'
    _description = "Partner Notice"

    partner_id = fields.Many2one('res.partner', string='Customer')
    phone = fields.Char(related='partner_id.phone', string='Phone', store=True)
    # partner_name = fields.Char(related='partner_id.name', string='Customer Name', store=True)
    date = fields.Datetime('Date')
    name = fields.Char('Title', translate=True)
    body = fields.Text('Body')