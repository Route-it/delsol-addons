# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date, datetime
import pytz
import logging

class vehicle_notify(models.Model):

    _auto = False
    _name = "delsol.vehicle_notify"
    
    @api.model
    def process(self):

        logging.info("iniciando cron on_ready_for_programmed")
        events = self.env['delsol.event'].search([('active','=',True),('code','=','on_ready_for_programmed'),('emails','!=',False)])
        logging.debug("events:"+str(events.ids))
        
        if (len(events.ids) >0 ):

            vehicles = self.env['delsol.vehicle'].search([
                                               ('priority_of_chequed_request','=','high'),
                                               ('state','in',('ready_for_programmed','not_chequed')),
                                               ])

                                   
            if (len(vehicles.ids) >0 ):
                body = ''
                for i in ('auto','camion'):
                    for j in ('ready_for_programmed','not_chequed'):
            
                        vehicles_for_body = vehicles.filtered(lambda r: (r.state == j) & (r.modelo.vehicle_type == i))
                        
                        if i == 'auto':
                            istr = 'autos'
                        else:
                            istr = 'camiones'
                        if j == 'ready_for_programmed':
                            body += "Listado de "+istr+" para programar (Prioridad:Alta):\n\n<br><br>"
                        else:
                            body += "Listado de "+i+" para chequear (Prioridad:Alta):\n\n<br><br>"
                            
                        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                        for v in vehicles_for_body:
                            if bool(v.modelo.description):
                                modelo = (v.modelo.description[:15] + '..') if len(v.modelo.description) > 15 else v.modelo.description
                            else:
                                modelo = ''
                            fecha_hora_solicitud_chequeo = ''
                            if bool(v.date_for_calendar):
                                fecha_hora_solicitud_chequeo = datetime.strptime(v.date_for_calendar, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                            if bool(v.client_id):
                                body += v.client_id.name +" | " 
                            body += modelo +" | " 
                            if bool(fecha_hora_solicitud_chequeo):
                                body += "F.Solicitud: " + fecha_hora_solicitud_chequeo  
                            body +=" | cha:"+v.nro_chasis
                            body +=" | "
                            body +="<a href='"
                            body += '%s/web?db=%s#id=%s&view_type=form&model=delsol.vehicle' % (base_url, self._cr.dbname, v.id)
                            body +="' target='_blank'>acceso</a>"
                            body +="\n<br>"
                
                        body += "\n\n\n<br><br><br>"

                
                delsol_mail_server = self.env['delsol.mail_server']
                delsol_mail_server.send_mail("Vehiculos para programar",body,[(e) for e in events.emails.split(",")])
                
            else:
                logging.info("Cron on_ready_for_programmed: nada para enviar.")
            logging.info("Cron on_ready_for_programmed completado.")
        else:
            logging.info("Cron on_ready_for_programmed: nada para enviar.")
