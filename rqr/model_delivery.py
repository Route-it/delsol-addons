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

class delsol_delivery(models.Model):
    
    _name = "delsol.delivery"

    name = fields.Char(compute="name_get", store=True, readonly=True)
     
    client_id = fields.Many2one('res.partner',string="Cliente",domain = [('customer','=','True')], help = "Cliente asociado al vehiculo")

    vehicle_id = fields.Many2one('delsol.vehicle',string="Vehiculo", help = "Vehiculo entregado")

    delivery_date = fields.Datetime(string="Fecha de entrega")
    
    delay = fields.Integer(default=1)
    
    color = fields.Integer(default=100)

    vendor_id = fields.Many2one("res.partner",String="Vendedor",domain=[("customer",'=',False),("vendor",'=','True')])

    call_ids = fields.One2many('delsol.call','delivery_id',string="Contactos al cliente", help = "Contactos con el cliente")
    rqr_ids = fields.One2many('delsol.rqr','delivery_id',string="RQRs", help = "RQR asociados a esta entrega")

    quick_touch = fields.Many2one("delsol.quick_touch",String="Quick Touch")

    contacted = fields.Boolean("Contactado",compute="is_contacted",store=True)

    answered_poll = fields.Boolean("Contesto encuesta?")


    @api.depends('call_ids')
    def is_contacted(self,cr, uid, ids, context=None):
        is_contacted = False
        for record in self.browse(cr, uid, ids, context=context):
            for call in record.call_ids:
                is_contacted = is_contacted | call.contacted
                if is_contacted: break
            
            record.contacted = is_contacted
        return is_contacted

    @api.depends('client_id','delivery_date','vehicle_id')
    def name_get(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            record.name = self.name_get_str(record)
            res.append((record.id, self.name_get_str(record)))
        return res
    
    def name_get_str(self,record):
            cliente = ''
            vehiculo = ''
            fecha = ''
                
            if record.client_id:
                cliente = str(record.client_id.name_get_str(record.client_id)) or ''
            
            if record.delivery_date:
                fecha = str(record.delivery_date[0:10])
            
            if record.vehicle_id:
                vehiculo = str(record.vehicle_id.name_get_str(record.vehicle_id)) or ''

            return str(cliente) + '(' + str(vehiculo) + '), ' + fecha  
        
