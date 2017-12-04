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

class delsol_delivery_expired(models.Model):

    _auto = False
    
    _name = "delsol.delivery_of_day"
     
    @api.model
    def process(self):

        logging.info("iniciando cron on_delivery_of_day")
        events = self.env['delsol.event'].search([('active','=',True),('code','=','on_delivery_of_day'),('emails','!=',False)])
        logging.debug("events:"+str(events.ids))
        
        if (len(events.ids) >0 ):
            #hoy_00 = datetime.datetime.strptime(datetime.datetime.today(),"%Y-%m-%d")
            hoy_00 = datetime.datetime.today()
            manana_00 = hoy_00 + datetime.timedelta(days=1)
            
            
            #if valid_date_tmp > datetime.datetime.today():
            #if ((valid_date_tmp - datetime.timedelta(minutes=alarm.duration_minutes)) <= datetime.datetime.today()): 
            
            deliverys = self.env['delsol.delivery'].search([
                                               ('active','=',True),
                                               ('state','not in',('delivered','dispatched')),
                                               ('delivery_date','<',str(manana_00)[:10]),
                                               ('delivery_date','>=',str(hoy_00)[:10])
                                               ])
            
            if (len(deliverys.ids) >0 ):
            
                vendor_ids = deliverys.mapped('vendor_id')

                deliverys_assigned = deliverys.filtered(lambda r: (bool(r.vendor_id) != False))

                without_vendor = deliverys - deliverys_assigned

                logging.debug("deliverys:"+str(deliverys.ids))
    
                body = "Listado de entregas del dia:\n\n<br><br>"
        
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')

                user_tz = self.env.user.tz or pytz.utc
                local = pytz.timezone(user_tz)

                
                for v in vendor_ids:
                    body += "\n<br>\n<br>"
                    body += "Entregas de: <b>"+ v.name_related + "</b>:\n<br>\n<br> "
                    
                    delivery_v = deliverys_assigned.filtered(lambda dv: (dv.vendor_id == v))
                    
                    for d in delivery_v:
                    
                        if bool(d.vehicle_id.modelo.description):
                            modelo = (d.vehicle_id.modelo.description[:15] + '..') if len(d.vehicle_id.modelo.description) > 15 else d.vehicle_id.modelo.description
                        else:
                            modelo = ''

                        hora = pytz.utc.localize(datetime.datetime.strptime(d.delivery_date, '%Y-%m-%d %H:%M:%S')).astimezone(local).strftime('%H:%M')

                        #fecha_hora = datetime.datetime.strptime(d.delivery_date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                        #fecha_hora = d.delivery_date[:16]
                        if bool(d.client_id):
                            body += d.client_id.name +" | " 
                            body += ' / '.join(x for x in (d.client_id.phone,d.client_id.mobile) if x) +" | "  
                        body += modelo +" | " 
                        body += hora 
                        body +="hs | "
                        body +="<a href='"
                        body += '%s/web?db=%s#id=%s&view_type=form&model=delsol.delivery' % (base_url, self._cr.dbname, d.id)
                        body +="' target='_blank'>acceso</a>"
                        body +="\n<br>"
        
                body += "\n\n\n<br><br><br>"

                body += "Listado de entregas sin vendedor asignado:\n\n<br><br>"
        
                for d in without_vendor:
                    if bool(d.vehicle_id.modelo.description):                    
                        modelo = (d.vehicle_id.modelo.description[:15] + '..') if len(d.vehicle_id.modelo.description) > 15 else d.vehicle_id.modelo.description
                    else:
                        modelo = ''
                    hora = pytz.utc.localize(datetime.datetime.strptime(d.delivery_date, '%Y-%m-%d %H:%M:%S')).astimezone(local).strftime('%H:%M')
                    #fecha_hora = d.delivery_date[:16]
                    if bool(d.client_id):
                        body += d.client_id.name +" | "
                        body += ' / '.join(x for x in (d.client_id.phone,d.client_id.mobile) if x) +" | "  
                    body += modelo +" | " 
                    body += hora 
                    body +="hs | "
                    body +="<a href='"
                    body += '%s/web?db=%s#id=%s&view_type=form&model=delsol.delivery' % (base_url, self._cr.dbname, d.id)
                    body +="' target='_blank'>acceso</a>"
                    body +="\n<br>"
        
                body += "\n\n\n<br><br><br>"


                delsol_mail_server = self.env['delsol.mail_server']
                delsol_mail_server.send_mail("Entregas del dia",body,[(e) for e in events.emails.split(",")])


            else:
                logging.info("Cron on_delivery_of_day: nada para enviar.")
            logging.info("Cron on_delivery_of_day completado.")
        else:
            logging.info("Cron on_delivery_of_day: nada para enviar.")
        