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
    
    _name = "delsol.delivery"

    _inherit = ["mail.thread", "ir.needaction_mixin"]

    name = fields.Char(compute="name_get", store=True, readonly=True)
    
    active = fields.Boolean("Registro Activo", help = "Si se deja sin seleccionar, el registro quedará archivado.", default=True)
     
    client_id = fields.Many2one('res.partner',string="Cliente",domain = [('customer','=','True')], help = "Cliente asociado al vehiculo",required=True,
                                ondelete='cascade',write=['base.user_root','rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'],
                                track_visibility='onchange')

    vehicle_id = fields.Many2one('delsol.vehicle',string="Vehiculo", help = "Vehiculo",required=True,track_visibility='onchange',
                                 write=['base.user_root','rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])

    client_date = fields.Datetime("Fecha y horario de cita",required=True)
    
    delivery_date = fields.Datetime("Fecha y horario de entrega",required=True,write=['base.user_root','rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])

    create_date = fields.Datetime("Fecha de alta")
    
    sector = fields.Selection([("ovalo","Plan Óvalo"),("especial","Venta Especial"),("tradicional","Venta Tradicional"),("camiones","Camiones")],
                              string="Sector",required="True")
    
    delay = fields.Integer(default=1)
    
    color = fields.Integer(default=100)

    vendor_id = fields.Many2one("hr.employee",String="Vendedor",write=['base.user_root','rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])
    
    applay_rqr = fields.Boolean("Aplica RQR",write=['base.user_root','rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])
    
    call_ids = fields.One2many('delsol.call','delivery_id',string="Contactos al cliente", help = "Contactos con el cliente",groups="base.user_root,rqr.group_name_rqr_delivery_resp,rqr.group_name_rqr_contact_resp,rqr.group_name_rqr_administrator")
    
    rqr_ids = fields.One2many('delsol.rqr','delivery_id',string="RQRs", help = "RQR asociados a esta entrega",groups="base.user_root,rqr.group_name_rqr_contact_resp,rqr.group_name_rqr_administrator")

    contacted = fields.Boolean(string="Contactado",compute="is_contacted",store=True)
    
    turn_duration = fields.Float("Duración de turno",compute="depends_vehicle",store=True)
    turn_duration_from_child = fields.Integer("Duración de turno")
    
    answered_poll = fields.Boolean("Contesto encuesta?")
    sales_asistance = fields.Integer("Asesor de ventas",default=3,help="Califique del 1 al 5")
    payment_experience = fields.Integer("Experiencia de pago",default=3,help="Califique del 1 al 5")
    compliance = fields.Integer("Nivel de Cumplimiento",default=3,help="Califique del 1 al 5")
    delivery_process = fields.Integer("Proceso de entrega",default=3,help="Califique del 1 al 5")
    love_dealer = fields.Integer("Adorar al concesionario",default=3,help="Califique del 1 al 5")
    defense_dealer = fields.Integer("Defensa",default=3,help="Califique del 1 al 5")
    comment_poll = fields.Text("Comentaro")
    poll_rqr_id = fields.Many2one("delsol.rqr", string="RQR", readonly=True)
    vehicle_chasis = fields.Char("Chasis",related="vehicle_id.nro_chasis")
    vehicle_color = fields.Char("Color",related="vehicle_id.color.name")
    client_email = fields.Char(related="client_id.email")
    
    client_arrival = fields.Datetime("Horario de llegada de cliente", readonly=True)
    
 
    state = fields.Selection([('new','Nueva'),
                              ('reprogrammed','Reprogramada'),
                              ('dispatched','Despachado'),
                              ('delivered','Entregado')],string="Estado",default="new",readonly=True)
    olddate = fields.Datetime()
    tae_stamp = fields.Datetime("Fecha y hora de carga de TAE",help="Fecha y hora de carga de TAE para saber cuándo aproximadamente llega la encuesta")

    reprogramming_ids = fields.One2many("delsol.reprogramming","delivery_id",readonly=True)


    @api.multi
    def send_report_turn_to_client(self):
        self.ensure_one()

        if (self.client_email):
            #generar el comprobante y enviarlo por mail como attachment
            report_obj = self.env['report']
            mail_obj = self.env['ir.mail_server']
    
            report = report_obj._get_report_from_name('rqr.report_turn')
            filename = "%s.%s" % (report.name, "pdf")
    
    
            filecontents = report_obj.get_pdf(self, 'rqr.report_turn')
    
    
            body = "Estimado/a "+self.client_id.name +":\n \t Le informamos que la entrega de su "
             
            body += self.vehicle_id.marca +" " +self.vehicle_id.modelo.description+" ha sido programada. "
            body += "Adjuntamos el comprobante con todos los datos necesarios."
            body += "\n\n Le deseamos que tenga una buena jornada,\n Del Sol Automotor."
    
            IrMailServer = self.env['ir.mail_server']
            msg = IrMailServer.build_email(
                email_from="entregade0km@delsolautomotor.com.ar",
                email_to=[("diego.richi@gmail.com")],
                subject="Del Sol Automotor informa",
                body= body,
                attachments = [(filename, filecontents)],
                reply_to="entregade0km@delsolautomotor.com.ar",
                )
            
    
            """msg_id = IrMailServer.send_email(message=msg,
                              smtp_server="smtp.office365.com",
                              smtp_encryption="starttls",
                              smtp_port="587",
                              smtp_user="entregade0km@delsolautomotor.com.ar",
                              smtp_password="Kapu2113"
                              )
            """
            self.env.user.notify_info('El comprobante se envio con exito!.')
        else:
            self.env.user.notify_info('El cliente no posee el email cargado.')

                
    @api.multi
    def download_report_turn(self):
        self.ensure_one()
        result_search = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=',self._name)])
        
        #si no hay nada, hay que generarlo
        
        if len(result_search)==0:
            #generar el comprobante y guardarlo como attachment
            report_obj = self.env['report']

            
            #FUNCIONA!
            #pdf = report_obj.get_pdf(self, 'rqr.report_turn')
            
            #Devuelve HTML            
            #report_obj.render('rqr.report_turn', docargs)
            
            action  = report_obj.get_action(self, 'rqr.report_turn')
            
            return action 
            """
                {
            
                'type' : 'ir.actions.act_url',
                
                'url': '/report/download',
                
                'target': 'self',
            
            }
            """
        
        return {

            'type' : 'ir.actions.act_url',
            
            'url': '/web/content/' + str(result_search.id) +'?download=true',
            
            'target': 'self',
        
        }

    @api.model
    def default_get(self, fields):
        res = super(delsol_delivery, self).default_get(fields)
        if self._context.get('vehicle_id'):
            if 'vehicle_id' in fields:
                res.update({'vehicle_id': self._context.get('vehicle_id')})
        return res

    
    def set_new(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'new'
    
    @api.one
    def set_delivered(self):
        if (self.vehicle_id.state  in ('ready_for_delivery','dispatched')):
            if ((bool(self.vehicle_id.patente)) & (bool(self.vehicle_chasis))):  
                if ((len(self.vehicle_id.patente)>0) & (len(self.vehicle_chasis)>0)):  
                    self.state = 'delivered'
                    self.vehicle_id.state = 'delivered'
                    self.vehicle_id.priority_of_chequed_request = 'normal'
                else:
                    self.env.user.notify_warning("El vehiculo no posee patente o nro de chasis cargado.")
                    raise ValidationError("El vehiculo no posee patente o nro de chasis cargado.")
                    return
            else:
                self.env.user.notify_warning("El vehiculo no posee patente o nro de chasis cargado.")
                raise ValidationError("El vehiculo no posee patente o nro de chasis cargado.")
                return
        else:
            self.env.user.notify_warning("El vehiculo no esta listo para entregar.")
            raise ValidationError("El vehiculo no esta listo para entregar.")
            return
            
            
    
    @api.one
    def set_dispatched(self):
        self.state = "dispatched"
        self.vehicle_id.state = 'dispatched'
        self.vehicle_id.priority_of_chequed_request = 'normal'
        self.client_arrival = self.delivery_date

    def set_close(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'closed'

    @api.onchange('contacted')
    def verify_state(self):
        if self.contacted & (self.state == 'new' | self.state == 'delivered' ):
            self.state = 'contacted'
   
    @api.constrains('delivery_date')
    def set_reprogrammed(self):
        if (self.delivery_date != self.olddate) and (self.olddate is not False):
            self.state = 'reprogrammed'
        self.olddate = self.delivery_date
        self.vehicle_id.priority_of_chequed_request = 'normal'

    @api.one
    def stamp_tae(self):
        if not self.tae_stamp:
            self.tae_stamp = fields.Datetime.now()
        

#    def chek_vehicle_not_delivered(self, cr, uid, ids, context=None):
#        result_search = self.pool.get('delsol.delivery').search(cr, uid, [('vehicle_id','=',self.vehicle_id)], context=context)
#        if len(result_search)>0:
#            result_search

    @api.constrains('vehicle_id')
    def chek_vehicle_ready_for_delivery(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if bool(record.vehicle_id):
                result_search = self.pool.get('delsol.delivery').search(cr, uid, [('vehicle_id','=',record.vehicle_id.id)], context=context)
                if len(result_search)>1:
                    raise ValidationError("El vehiculo ya fue entregado")
                    return
                if (record.vehicle_id.state not in ("to_be_delivery","ready_for_delivery")):
                    raise ValidationError("El vehiculo no esta listo para programar la entrega.")
                    return


    @api.depends('call_ids')
    def is_contacted(self,cr, uid, ids, context=None):
        is_contacted = False
        for record in self.browse(cr, uid, ids, context=context):
            for call in record.call_ids:
                is_contacted = is_contacted | call.contacted
                if is_contacted: break
            
            record.contacted = is_contacted
        return is_contacted

    @api.depends('client_id','delivery_date','vehicle_id')
    def name_get(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            record.name = self.name_get_str(record)
            res.append((record.id, self.name_get_str(record)))
        return res
    
    @api.depends('vehicle_id')
    def depends_vehicle(self):
        self.turn_duration = float(self.vehicle_id.modelo.turn_duration)/60

        
    @api.onchange('vehicle_id')
    def change_vehicle(self):
        if bool(self.vehicle_id.modelo.vehicle_type):
            if self.vehicle_id.modelo.vehicle_type == 'camion':
                self.sector = 'camiones'
            else:
                self.sector = ''
        
    def name_get_str(self,record):
            cliente = ''
            vehiculo = ''
            fecha = ''
                
            if record.client_id:
                cliente = str(record.client_id.name_get_str(record.client_id)) or ''
            
            if record.delivery_date:
                fecha = str(record.delivery_date[0:10])
            
            if record.vehicle_id:
                vehiculo = str(record.vehicle_id.name_get_str(record.vehicle_id)) or ''

            return str(cliente) + '(' + str(vehiculo) + '), ' + fecha  
        
    def make_poll_rqr(self,cr, uid, ids, context=None):
        rqr_obj = self.pool['delsol.rqr']
        #rqr_state_obj = self.pool['delsol.rqr_state']
        #rqr_state = rqr_state_obj.search(cr, uid, [('sequence','=', 0)])
        
        
        for delivery in self.browse(cr, uid, ids, context=context):
        #check if delivery is delivered.
            if delivery.state != 'delivered':
                raise Warning('La entrega debe estar en estado "Entregado".')
                return
            
            message = 'Ya se posee una rqr generada.'
            
            if not bool(delivery.poll_rqr_id):
                defaults = {'delivery_id': delivery.id,'state':'new','sector':delivery.sector}
                
                target_rqr =  rqr_obj.create(cr, uid, defaults, None)
                
                delivery.poll_rqr_id = target_rqr
                message = 'Se genero correctamente la RQR.'


            """
            warning = {
                        'title': 'Mensaje !',
                        'message': message
                     }
            """
        
            self.env.user.notify_info(message)
    
            res = {'value': {}}
            warning = {'warning': {
                    'title': 'Mensaje',
                    'message': message,
                    }}        
            res.update(warning)
    
            #return {'warning': warning}
            #return res
            return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                    }
    @api.one
    def reprogram(self,reprogram):
        new_reprogramming = self.env['delsol.reprogramming'].create({'from_date':self.client_date,'to_date':reprogram.new_date,
                                                                     'responsible':reprogram.responsible,'reason':reprogram.reason,
                                                                 'delivery_id':self.id})
        self.reprogramming_ids |= new_reprogramming
        self.client_date = reprogram.new_date
        self.delivery_date = reprogram.new_delivery_date
        self.client_arrival = False
        self.state = "reprogrammed"
        
        
        
        body = '%s ha modificado la programacion de %s a %s.' % (self.env.user.name, new_reprogramming.from_date,new_reprogramming.to_date)

        super(delsol_delivery,self).message_post(body=body)

        self.env.user.notify_info('Se ha reprogramado la entrega.')

        return {'type': 'ir.actions.act_window_close'}
    
    @api.one
    def stamp_client_arrival(self):
        self.client_arrival = fields.Datetime.now()

        try:
            smsuser = "DELSOLAUTOMOTOR"
            smsclave = "Timberline838"
            smsnro = "2974139563" #  Sergio Bellido
            modelo = (self.vehicle_id.modelo.description[:15] + '..') if len(self.vehicle_id.modelo.description) > 15 else self.vehicle_id.modelo.description
            
            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            
            hora = pytz.utc.localize(datetime.datetime.strptime(self.delivery_date, '%Y-%m-%d %H:%M:%S')).astimezone(local).strftime('%H:%M')

	    smstexto = "El cliente "+self.client_id.name +" ha arribado. Hora entrega: "+ hora +". "+modelo +" " + self.vehicle_color +" " + self.vehicle_id.patente
            
            r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS=" +smsnro + "&TEXTO=" + smstexto + "&USUARIO=" + smsuser + "&CLAVE=" + smsclave)
            print 'r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS="' +smsnro + '&TEXTO=' + smstexto + '&USUARIO=' + smsuser + '&CLAVE=' + smsclave +")"

            self.env.user.notify_info('Se ha notificado por sms al responsable de entregas.')
            
            print r.status_code
            print r.headers
            print r.content
                
        except:
            print "Unexpected error!"

        try:
            smsuser = "DELSOLAUTOMOTOR"
            smsclave = "Timberline838"
            smsnro = self.client_id.mobile if self.client_id.mobile else self.client_id.phone
            
            if (smsnro[:1] == '0'):
                smsnro = smsnro[1:]
            
            if (smsnro[:2] == '15'):
                smsnro = smsnro[2:]
                smsnro = '297'+smsnro

            if not ((smsnro[:1] != '2') or (smsnro[:1] != '3') or (smsnro[:1] != '1')):
                smsnro = '297'+smsnro
            
            smsnro = smsnro.replace(' ','').replace('-','').replace('/','')
            
            
            smstexto = "Del sol le da la bienvenida y le desea muchas felicidades. La clave de la wifi DEL_SOL_CLIENTES es ford2017"
            #"llego el cliente " + cliente_id.nombre
            
            #r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS=" +smsnro + "&TEXTO=" + smstexto + "&USUARIO=" + smsuser + "&CLAVE=" + smsclave)    
            #print 'r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS="' +smsnro + '&TEXTO=' + smstexto + '&USUARIO=' + smsuser + '&CLAVE=' + smsclave +")"

            #print r.status_code
            #print r.headers
            #print r.content
        except:
            print "Unexpected error!"

        # ENVIAR MAIL DIRECTO A TRAVES DE X SERVIDOR
        """
        IrMailServer = self.env['ir.mail_server']
        msg = IrMailServer.build_email(
            email_from="sistemas@delsolautomotor.com.ar",
            email_to=[("diego.richi@gmail.com"),("lvelasques@delsolautomotor.com.ar")],
            subject="Te ganaste un auto!",
            body="viste que rapido va esto!",
            reply_to="diego.richi@gmail.com",
            subtype='plain',
            subtype_alternative='plain'
            )
           :param string email_from: sender email address
           :param list email_to: list of recipient addresses (to be joined with commas) 
           :param string subject: email subject (no pre-encoding/quoting necessary)
           :param string body: email body, of the type ``subtype`` (by default, plaintext).
                               If html subtype is used, the message will be automatically converted
                               to plaintext and wrapped in multipart/alternative, unless an explicit
                               ``body_alternative`` version is passed.
           :param string body_alternative: optional alternative body, of the type specified in ``subtype_alternative``
           :param string reply_to: optional value of Reply-To header
           :param string object_id: optional tracking identifier, to be included in the message-id for
                                    recognizing replies. Suggested format for object-id is "res_id-model",
                                    e.g. "12345-crm.lead".
           :param string subtype: optional mime subtype for the text body (usually 'plain' or 'html'),
                                  must match the format of the ``body`` parameter. Default is 'plain',
                                  making the content part of the mail "text/plain".
           :param string subtype_alternative: optional mime subtype of ``body_alternative`` (usually 'plain'
                                              or 'html'). Default is 'plain'.
           :param list attachments: list of (filename, filecontents) pairs, where filecontents is a string
                                    containing the bytes of the attachment
           :param list email_cc: optional list of string values for CC header (to be joined with commas)
           :param list email_bcc: optional list of string values for BCC header (to be joined with commas)
           :param dict headers: optional map of headers to set on the outgoing mail (may override the
                                other headers, including Subject, Reply-To, Message-Id, etc.)
           :rtype: email.message.Message (usually MIMEMultipart)
           :return: the new RFC2822 email message

        
        msg_id = IrMailServer.send_email(message=msg,
                          smtp_server="smtp.office365.com",
                          smtp_encryption="starttls",
                          smtp_port="587",
                          smtp_user="sistemas@delsolautomotor.com.ar",
                          smtp_password="Runa9366"
                          )
        
        print msg_id
        """



        #ENVIAR SMS DIRECTO A TRAVES DE SMSMASIVOS        
        """       
        :param message: the email.message.Message to send. The envelope sender will be extracted from the
                        ``Return-Path`` (if present), or will be set to the default bounce address.
                        The envelope recipients will be extracted from the combined list of ``To``,
                        ``CC`` and ``BCC`` headers.
        :param mail_server_id: optional id of ir.mail_server to use for sending. overrides other smtp_* arguments.
        :param smtp_server: optional hostname of SMTP server to use
        :param smtp_encryption: optional TLS mode, one of 'none', 'starttls' or 'ssl' (see ir.mail_server fields for explanation)
        :param smtp_port: optional SMTP port, if mail_server_id is not passed
        :param smtp_user: optional SMTP user, if mail_server_id is not passed
        :param smtp_password: optional SMTP password to use, if mail_server_id is not passed

        smsuser = "DELSOLAUTOMOTOR"
        smsclave = "Timberline838"
        smsnro = "2974924655"
        smstexto = "llego el cliente " + cliente_id.nombre
        
        r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS=" +smsnro + "&TEXTO=" + smstexto + "&USUARIO=" + smsuser + "&CLAVE=" + smsclave)    
        print r.status_code
        print r.headers
        print r.content
        
        """
        
