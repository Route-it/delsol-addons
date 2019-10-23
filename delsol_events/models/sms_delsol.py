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
                #r = requests.get(self.url % ("DELSOLCAMIONESSERVICIO","DELSOLCAMIONESSERVICIO388") + body)
                r = requests.get(self.url % (self.usuario_sms,self.clave_sms) + body)
            
            if (len(r.content)>0) & ("agotado" in r.content):
                
                body = "Mensaje de ODOO: Se agotaron los sms del usuario: " + self.usuario_sms +" en la plataforma SMS MASIVOS <br><br>"
                body += "<a href='http://servicio.smsmasivos.com.ar/ver_reporte_generico.asp?relogin=1&usuario=DELSOLAUTOMOTOR&clave=TIMBERLINE838' target='_blank'>Ir a modificar saldos.</a>"
                
                delsol_mail_server = self.env['delsol.mail_server']
                delsol_mail_server.send_mail("Se agotaron los sms del usuario %s" %  self.usuario_sms,body,[("diego@routeit.com.ar")])
                #delsol_mail_server.send_mail("Se agotaron los sms del usuario %s" %  self.usuario_sms,body,[("tguerrero@delsolautomotor.com.ar")])
                
                return -1,r.content #2974924655: se han agotado los SMS contratados.
            else:
                return r.status_code,r.content
        except Exception as e:
            print "Unexpected error!"


