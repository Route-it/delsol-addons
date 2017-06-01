# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import datetime
import logging

_logger = logging.getLogger(__name__)

class delsol_process_events(models.Model):
    
    _name = "delsol.process_events"
     
    @api.model
    def process(self):

        logging.info("iniciando cron on_delivery_expired")
        events = self.env['delsol.event'].search([('active','=',True),('code','=','on_delivery_expired'),('emails','!=',False)])
        logging.debug("events:"+str(events.ids))
        
        if (len(events.ids) >0 ):
            #hoy_00 = datetime.datetime.strptime(datetime.datetime.today(),"%Y-%m-%d")
            hoy_00 = datetime.datetime.today()
            ayer_00 = hoy_00 - datetime.timedelta(days=1)
            
            
            #if valid_date_tmp > datetime.datetime.today():
            #if ((valid_date_tmp - datetime.timedelta(minutes=alarm.duration_minutes)) <= datetime.datetime.today()): 
            
            deliverys = self.env['delsol.delivery'].search([
                                               ('active','=',True),
                                               ('state','not in',('delivered','dispatched')),
                                               ('delivery_date','<',str(hoy_00)[:10])
                                               ])
            if (len(deliverys.ids) >0 ):
            
    
                logging.debug("deliverys:"+str(deliverys.ids))
    
                body = "Listado de entregas vencidas que necesitan accion:\n\n<br><br>"
        
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                for d in deliverys:
                    modelo = (d.vehicle_id.modelo.description[:15] + '..') if len(d.vehicle_id.modelo.description) > 15 else d.vehicle_id.modelo.description
                    fecha_hora = datetime.datetime.strptime(d.delivery_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                    body += d.client_id.name +" | " 
                    body += modelo +" | " 
                    body += fecha_hora 
                    body +=" | cha:"+d.vehicle_chasis 
                    body +=" | "
                    body +="<a href='"
                    body += '%s/web?db=%s#id=%s&view_type=form&model=delsol.delivery' % (base_url, self._cr.dbname, d.id)
                    body +="' target='_blank'>acceso</a>"
                    body +="\n<br>"
        
                body += "\n\n\n<br><br><br>"
                
                IrMailServer = self.env['ir.mail_server']
                msg = IrMailServer.build_email(
                    email_from="sistemas@delsolautomotor.com.ar",
                    email_to=[(e) for e in events.emails.split(",")],
                    subject="Aviso de entregas vencidas",
                    body=body,
                    subtype="html",
                    reply_to="",
                    )
        
                logging.debug("Cuerpo del mail:"+body)
        
                msg_id = IrMailServer.send_email(message=msg,
                          smtp_server="smtp.office365.com",
                          smtp_encryption="starttls",
                          smtp_port="587",
                          smtp_user="sistemas@delsolautomotor.com.ar",
                          smtp_password="Runa9366"
                          )
            else:
                logging.info("Cron on_delivery_expired: nada para enviar.")
            logging.info("Cron on_delivery_expired completado.")
        else:
            logging.info("Cron on_delivery_expired: nada para enviar.")
        