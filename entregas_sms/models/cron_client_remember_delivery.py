# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date, datetime
import pytz


import datetime
import logging

_logger = logging.getLogger(__name__)

class delsol_client_remember_delivery(models.Model):

    _auto = False
    
    _name = "delsol.client_remember_delivery"
     
    @api.model
    def process(self):

        logging.info("iniciando cron client_remember_delivery")
        send_remember_to_client = self.env['delsol.config'].search([('code','=','send_remember_to_client')]).value
        send_remember_to_client_b = eval(send_remember_to_client.capitalize()) 
        
        logging.debug("send_remember_to_client_b:"+str(send_remember_to_client_b))
        
        hoy_00 = datetime.datetime.today()
        manana_00 = hoy_00 + datetime.timedelta(days=1)
        pasado_manana_00 = hoy_00 + datetime.timedelta(days=2)
        
        deliverys = self.env['delsol.delivery'].search([
                                           ('active','=',True),
                                           ('state','not in',('delivered','dispatched')),
                                           ('delivery_date','<',str(pasado_manana_00)[:10]),
                                           ('delivery_date','>=',str(manana_00)[:10])
                                           ])
        
            
        for d in deliverys:
            message = u"Mañana es la entrega de su " + d.vehicle_id.marca + d.get_delivery_datetime(d.client_date)[5:] +"."
            if not (("batea" in d.client_id.name.lower()) or ("del sol" in d.client_id.name.lower())):
                if d.vehicle_id.modelo.vehicle_type == 'auto':
                    d.send_sms(message)
                    d.message_post(body="Se ha notificado por sms al cliente: "+message)

        logging.info("Finalizo el cron de recordatorios a clientes.")
        

        