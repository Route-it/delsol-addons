# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api

import logging
import requests

_logger = logging.getLogger(__name__)

class delsol_sms_server(models.Model):
    
    _name = "delsol.sms_server"
    
    name = fields.Char("Nombre")

    usuario_sms = fields.Char("Usuario")

    clave_sms = fields.Char("Clave")
    
    url = "http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&USUARIO=%s&CLAVE=%s"
    
    @api.model
    def send_sms(self,message,smsnro): 

        try:
            smsnro = "2974924655"
            
            _logger.info("enviando mensaje sms a:"+smsnro+" / "+ message)

            max_chars = 160
            message_array = [message[i:i+max_chars] for i in range(0, len(message), max_chars)]                
            for m in message_array: 
                body = "&TOS=%s&TEXTO=%s"% (smsnro,m)
                r = requests.get(self.url % (self.usuario_sms,self.clave_sms) + body)
            print r.content
            return r.status_code,r.content
        except Exception as e:
            print "Unexpected error!"


