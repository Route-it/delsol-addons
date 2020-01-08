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

class delsol_delivery_approaching(models.Model):

    _auto = False
    
    _name = "delsol.delivery_approaching"
     
    @api.model
    def process(self):

        logging.info("iniciando cron delivery_approaching")
        events = self.env['delsol.event'].search([('active','=',True),('code','=','delivery_approaching'),('emails','!=',False)])
        logging.debug("events:"+str(events.ids))
        
        if (len(events.ids) >0 ):
            days_approaching = self.env['delsol.config'].search([('code', '=', 'delivery_approaching_days')]).value

            hoy_00 = datetime.datetime.today()
            days_approaching_date = hoy_00 + datetime.timedelta(days=int(days_approaching))
            
            
            #entregas que le faltan X dias para la promesa de entrega y no estan entregadas.
            
            all_vehicles_approaching = self.env['delsol.vehicle'].search([
                                               ('state','not in',('delivered','dispatched')),
                                               ('delivery_date_promess','<=',str(days_approaching_date)[:10]),
                                               ('delivery_date_promess','>=',str(hoy_00)[:10])
                                               ])
            result = self.env['delsol.delivery'].search([('vehicle_id','in',all_vehicles_approaching.mapped('id'))])
            if len(result)>0:
                mapped_delivery_vehicle = result.mapped('vehicle_id.id')
                vehicles = all_vehicles_approaching.filtered(lambda v: v.id not in mapped_delivery_vehicle)
            else:
                vehicles = all_vehicles_approaching
            
            if (len(vehicles.ids) >0 ):

                logging.debug("vehicles:"+str(vehicles.ids))
    
                body = "Listado de vehiculos proximos a entregar sin accion de entrega:\n\n<br><br>"
        
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')

                user_tz = self.env.user.tz or pytz.utc
                local = pytz.timezone(user_tz)

                vehicles = vehicles.sorted(key=lambda v: v.delivery_date_promess)
                for v in vehicles:
                    body += "\n<br>\n<br>"
                    
                    if bool(v.modelo.description):
                        modelo = (v.modelo.description[:15] + '..') if len(v.modelo.description) > 15 else v.modelo.description
                    else:
                        modelo = ''

                    fecha = v.delivery_date_promess[:10]
                    if bool(v.client_id):
                        body += v.client_id.name +" | " 
                        body += ' / '.join(x for x in (v.client_id.phone,v.client_id.mobile) if x) +" <br> "  
                    body += "<b>"+ v.name + "</b><br>"
                    body += "Fecha Prometida de entrega: " 
                    body += fecha 
                    body +=" | "
                    body +="<a href='"
                    body += '%s/web?db=%s#id=%s&view_type=form&model=delsol.vehicle' % (base_url, self._cr.dbname, v.id)
                    body +="' target='_blank'>acceso</a>"
                    body +="\n<br>"
        
                body += "\n\n\n<br><br><br>"


                delsol_mail_server = self.env['delsol.mail_server']
                delsol_mail_server.send_mail("Entregas proximas a vencer",body,[(e) for e in events.emails.split(",")])


            else:
                logging.info("Cron delivery_approaching: nada para enviar.")
            logging.info("Cron delivery_approaching completado.")
        else:
            logging.info("Cron delivery_approaching: nada para enviar.")
        