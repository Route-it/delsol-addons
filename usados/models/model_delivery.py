# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api,_
from openerp.exceptions import ValidationError, Warning
from email.message import Message
from datetime import date, datetime
import pytz

import logging
import requests
import datetime

_logger = logging.getLogger(__name__)

class delsol_delivery(models.Model):
    

    _inherit = ["delsol.delivery"]

    client_deliver_used_vehicle = fields.Boolean(string="Entrega usado",help="Si esta activo, cuando el cliente llega, se envia un sms al resposable, para que se tome el vehiculo segun peritaje"
                                                 ,default=False)
        
    @api.one
    def stamp_client_arrival(self):
        super(delsol_delivery, self).stamp_client_arrival()

        if bool(self.client_deliver_used_vehicle):

            try:
                if self.vehicle_id.modelo.vehicle_type == 'auto':

                    smsnrololo = "2974139162" #  JM Lucero
        
                    user_tz = self.env.user.tz or pytz.utc
                    local = pytz.timezone(user_tz)
                    
                    hora = pytz.utc.localize(datetime.datetime.strptime(self.delivery_date, '%Y-%m-%d %H:%M:%S')).astimezone(local).strftime('%H:%M')
                    
                    message = "El cliente "+self.client_id.name +" ha arribado. Tiene un vehiculo usado para entregar"
        
                    delsol_sms_server = self.env['delsol.sms_server'].search([('name','=','ventas')])[0]
                    delsol_sms_server.send_sms(message,smsnrololo)
    
                    mensaje_dpto_usados = 'Se ha notificado por sms al responsable de usados para recibir dicho vehiculo.'
                    super(delsol_delivery,self).message_post(body=mensaje_dpto_usados)
                    self.env.user.notify_info(mensaje_dpto_usados)
                
            except:
                print "Unexpected error!"

        