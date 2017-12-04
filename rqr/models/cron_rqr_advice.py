# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from datetime import date, datetime
import pytz
import logging
import textwrap

class delsol_vehicle_notify(models.Model):

    _auto = False
    _name = "delsol.rqr_advice"
     
    @api.model
    def process(self):
        logging.info("iniciando cron rqr_advice")
        events = self.env['delsol.event'].search([('active','=',True),('code','=','rqr_advice')])
        logging.debug("events:"+str(events.ids))
        
        if (len(events.ids) >0 ):
            
            rqrs = self.env['delsol.rqr'].search([
                                               ('state','in',['new','progress'])
                                               ])
            
            if (len(rqrs.ids) >0 ):

                body = '<b><u>Listado de RQR sin asignar:</u></b>\n<br>\n<br>'

                base_url = self.env['ir.config_parameter'].get_param('web.base.url')

                rqr_assigned = rqrs.filtered(lambda r: (bool(r.responsible_id) != False))

                rqr_unassigned = rqrs - rqr_assigned
                
                for r in rqr_unassigned:
                    if bool(r.sector):
                        body += r.sector + " | "
                    body += "<b>Demora:</b> "+ str(r.delay_to_take_action) + " Dias | "
                    if bool(r.delivery_id.client_id.name):
                        body += r.delivery_id.client_id.name + " | " 
                    if bool(r.delivery_id.vehicle_id.modelo.short_name):
                        body += r.delivery_id.vehicle_id.modelo.short_name + " | " 
                    body +="<a href='"
                    body += '%s/web?db=%s#id=%s&view_type=form&model=delsol.rqr' % (base_url, self._cr.dbname, r.id)
                    body +="' target='_blank'>acceso</a>"
                    body += "\n<br><b>Comentario de llamados:</b> "
                    for i in r.call_ids.mapped("comment"):
                        if bool(i):                
                            body += " - " + "\n<br>                           ".join(x for x in textwrap.wrap(i, width=80))
                    body += " | \n<br><b>Comentario Encuesta:</b> "
                    if bool(r.comment_poll):
                        body += "\n<br>                     ".join(x for x in textwrap.wrap(r.comment_poll, width=80)) 

                    body += "\n<br>\n<br>\n<br>"
                body += "\n\n\n<br><br><br>"

                body += '<b><u>Listado de RQR pendientes por responsable:</u></b>\n<br>\n<br>'
                
                responsibles = rqr_assigned.mapped('responsible_id')
                
                
                for resp in responsibles:
                    body += "\n<br>\n<br>"
                    body += resp.name + ":\n<br>\n<br> "
                    
                    rqr_respon = rqr_assigned.filtered(lambda rq: (rq.responsible_id == resp))
                    
                    for rqr_r in rqr_respon:
                        #self.env['delsol.vehicle'].search([('id','=',rqr_r.delivery_id.vehicle_id.client_id)])
                        if bool(rqr_r.delivery_id.client_id.name):
                            body += rqr_r.delivery_id.client_id.name + " | " 
                        if bool(rqr_r.delivery_id.vehicle_id.modelo.short_name):
                            body += rqr_r.delivery_id.vehicle_id.modelo.short_name + " | " 
                        
                        body += "<b>Demora:</b> "+ str(rqr_r.delay_to_take_action) + " Dias | "
                        if bool(rqr_r.tipo_rqr):
                            body += "<b>Tipo:</b> "+ rqr_r.tipo_rqr.name + " | "

                        body +="<a href='"
                        body += '%s/web?db=%s#id=%s&view_type=form&model=delsol.rqr' % (base_url, self._cr.dbname, rqr_r.id)
                        body +="' target='_blank'>acceso</a>"
                        body +="\n<br>"
        
                    body += "\n\n<br><br>"

                delsol_mail_server = self.env['delsol.mail_server']
                delsol_mail_server.send_mail("Aviso de RQRs pendientes",body,[(e) for e in events.emails.split(",")])



        logging.info("finalizando cron rqr_advice")
