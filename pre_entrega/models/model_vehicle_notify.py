# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from datetime import date, datetime
import pytz
import logging

class delsol_vehicle_notify(models.Model):

    _inherit = ["delsol.vehicle"]
        
    @api.one    
    def ready_for_programmed(self):
        super(delsol_vehicle_notify, self).ready_for_programmed()

        users = self.env['res.users'].search([])

        if ((len(users.ids) >0)&(self.priority_of_chequed_request == "high")): 
            for u in users:
                if u.has_group("entregas.group_name_admin_entregas"):
                    msg = '%s Se ha chequeado.' % self.name
                    u.notify_info(msg)


    @api.multi
    def exec_cron(self):
        self.process()

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
                            modelo = (v.modelo.description[:15] + '..') if len(v.modelo.description) > 15 else v.modelo.description
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

                
                print body

                IrMailServer = self.env['ir.mail_server']
                msg = IrMailServer.build_email(
                    email_from="sistemas@delsolautomotor.com.ar",
                    #email_to=[(e) for e in events.emails.split(",")],
                    email_to=['diego.richi@gmail.com'],
                    subject="Vehiculos para programar",
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
                          smtp_password="Runa2503"
                          )

            else:
                logging.info("Cron on_ready_for_programmed: nada para enviar.")
            logging.info("Cron on_ready_for_programmed completado.")
        else:
            logging.info("Cron on_ready_for_programmed: nada para enviar.")
