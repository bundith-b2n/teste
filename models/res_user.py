# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    pos_ids = fields.Many2many('pos.config', string='Allowed Point of Sale')
    pos_id = fields.Many2one('pos.config', string='Default Point of Sale')


