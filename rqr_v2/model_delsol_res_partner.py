
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import logging
import subprocess

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    delivery_ids = fields.One2many('delsol.delivery','client_id',string="Vehiculos entregados", help = "Vehiculos entregados",
                                   read=['base.group_no_one'])

    email = fields.Char('Email')
    phone = fields.Char('Phone')
    mobile = fields.Char('Mobile')

    @api.constrains('phone','mobile')
    def validate_if_can_contact(self):
        if not(bool(self.phone) | bool(self.mobile)):
            raise ValidationError("Uno de los campos telefono o movil es requerido.")
            return

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.name = self.name.title()
    
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, self.name_get_str(record)))
        return res


    def name_get_str(self,record):
            name = ''
            cuit = ''
            delivery = ''
            
            if record.name:
                name = record.name
    
            if record.vat:
                cuit = record.vat or ''
            #if record.delivery_ids:
            #    delivery = (str(record.delivery.vehicle_id) +'('+ str(record.delivery.delivery_date) +'), rqr:'+ str(record.delivery.rqr_ids.count)) or ''
            if (len(cuit) > 0):
                return str(name.encode('utf8')) + '(' + str(cuit) + ')'  

            return str(name.encode('utf8'))  

