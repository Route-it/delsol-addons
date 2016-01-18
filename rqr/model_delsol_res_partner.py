
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    delivery_ids = fields.One2many('delsol.delivery','client_id',string="Vehiculos entregados", help = "Vehiculos entregados")

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
            return str(name) + '(' + str(cuit) + ')'# +str(delivery)  


