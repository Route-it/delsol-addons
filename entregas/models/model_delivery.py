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

    _order = "delivery_date desc"

    @api.model
    def _vehicle_id_domain(self):
        cond_one = ('state', 'in', ('to_be_delivery','ready_for_delivery','damage'))
        
        # vehiculos que no estan e entregado/despachado pero estan listos para entregar
        result_search = self.env['delsol.delivery'].search([('vehicle_id.state','in', ('to_be_delivery','ready_for_delivery')),
                                                            ('state','in',('new','reprogrammed'))])
        
        
        # entregas de vehiculos daniados, en cualquier estado (no deberian poder volver a programarse)
        # los vehiculos que se entregan "daniados" no se pasan a entregado cuando se entregan
        result_search |= self.env['delsol.delivery'].search([('vehicle_id.state','=', 'damage')])
        
        if len(result_search)>0:
            vehicle_ids_programmed = result_search.mapped('vehicle_id.id')
            cond_two = ('id','not in',vehicle_ids_programmed)
            return [cond_one,cond_two]
        return [cond_one]



    name = fields.Char(compute="name_get", store=True, readonly=True)
    
    active = fields.Boolean("Registro Activo", help = "Si se deja sin seleccionar, el registro quedará archivado.", default=True)
     
    client_id = fields.Many2one(related='vehicle_id.client_id',string="Cliente",required=True,readonly=True,
                                track_visibility='onchange')

    vehicle_id = fields.Many2one('delsol.vehicle',string="Vehiculo", help = "Vehiculo",required=True,track_visibility='onchange',
                                 domain=_vehicle_id_domain)

    client_vehicle_readonly = fields.Boolean(compute="_client_vehicle_readonly")

    client_date = fields.Datetime("Fecha y horario de cita",required=True)
    
    delivery_date = fields.Datetime("Fecha y horario de entrega",required=True)

    create_date = fields.Datetime("Fecha de alta")
    
    sector = fields.Selection([("ovalo","Plan Óvalo"),("especial","Venta Especial"),("tradicional","Venta Tradicional"),("camiones","Camiones")],
                              string="Sector",required="True")
    
    delay = fields.Integer(default=1)
    
    color = fields.Integer(default=100)

    vendor_id = fields.Many2one("hr.employee",String="Vendedor")
        
    turn_duration = fields.Float("Duración de turno",compute="depends_vehicle",store=True)
    turn_duration_from_child = fields.Integer("Duración de turno")
    
    vehicle_state = fields.Selection("Estado del vehiculo",related="vehicle_id.state")
    vehicle_chasis = fields.Char("Chasis",related="vehicle_id.nro_chasis")
    vehicle_color = fields.Char("Color",related="vehicle_id.color.name")
    vehicle_pass_predelivery_proccess = fields.Boolean(related="vehicle_id.pass_predelivery_proccess")
    
    button_delivery_visible = fields.Boolean(compute="_button_delivery_visible")
    
    client_email = fields.Char(related="client_id.email")
    
    client_arrival = fields.Datetime("Horario de llegada de cliente", readonly=True)
    
    state = fields.Selection([('new','Nueva'),
                              ('reprogrammed','Reprogramada'),
                              ('dispatched','Despachado'),
                              ('delivered','Entregado')],string="Estado",default="new",readonly=True)
    olddate = fields.Datetime()
    tae_stamp = fields.Datetime("Fecha y hora de carga de TAE",help="Fecha y hora de carga de TAE para saber cuándo aproximadamente llega la encuesta")

    reprogramming_ids = fields.One2many("delsol.reprogramming","delivery_id",readonly=True)

    comments = fields.Text("Anotaciones")


    def _button_delivery_visible(self):
        if (self.vehicle_pass_predelivery_proccess) & (self.state == 'delivered'):
                self.button_delivery_visible=False
                return
            
        if bool(self.client_arrival):
            if self.state not in ('new','reprogrammed','dispatched'):
                self.button_delivery_visible=False
                return
        else:
            if not bool(self.vehicle_pass_predelivery_proccess):
                    self.button_delivery_visible=False
                    return
            
        self.button_delivery_visible=True
         
        #self.vehicle_pass_predelivery_proccess #si True debe ser visible, si false, debe ser visible
        
        #('client_arrival','=',False),('state','not in',('new','reprogrammed','dispatched')),'|',('vehicle_pass_predelivery_proccess','=',False)


    @api.one
    def change_state(self,new_state):
        mybody = "El usuario "+ self.env.user.display_name +", ha cambiado el estado de "+self.state + " a "+ new_state.new_state +" fuera del circuito normal"
        self.message_post(body=mybody, subject="Cambio de estado de entrega")

        statement = eval("self.set_"+new_state.new_state)
        statement()
        #eval("self.set_new") 
        
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

    
    @api.one
    def set_new(self):
        self.client_arrival = False
        self.tae_stamp = False
        if (self.vehicle_id.state in ('delivered','dispatched')) & (self.state in ('delivered','dispatched')):
            self.vehicle_id.state = 'ready_for_delivery'
        self.state = 'new'
    
    @api.one
    def set_delivered(self):
        if (self.vehicle_id.state  in ('ready_for_delivery','dispatched')):
            if ((bool(self.vehicle_id.patente)) & (bool(self.vehicle_chasis))):  
                if ((len(self.vehicle_id.patente)>0) & (len(self.vehicle_chasis)>0)):  
                    self.state = 'delivered'
                    self.vehicle_id.state = 'delivered'
                    self.vehicle_id.priority_of_chequed_request = 'normal'
                    self.env.user.notify_info("Recuerde cargar la fecha de TAE en el sistema.")
                else:
                    self.env.user.notify_warning("El vehiculo no posee patente o nro de chasis cargado.")
                    raise ValidationError("El vehiculo no posee patente o nro de chasis cargado.")
                    return
            else:
                self.env.user.notify_warning("El vehiculo no posee patente o nro de chasis cargado.")
                raise ValidationError("El vehiculo no posee patente o nro de chasis cargado.")
                return
        else:
            if ((self.vehicle_id.state  in ('damaged')) & self.env.user.has_group('entregas.group_name_admin_entregas_damaged')):
                mybody = "El usuario "+ self.env.user.display_name +", autoriz&oacute; la entrega del veh&iacute;culo da&ntilde;ado"
                self.env.user.notify_warning("El vehiculo se entrega dañado.")
                self.env.user.notify_info("Recuerde cargar la fehca de TAE en el sistema.")
                self.message_post(body=mybody, subject="Entrega de Vehiculo dañado")
                self.state = 'delivered'
                #se deja en estado damaged
                #self.vehicle_id.state = 'delivered'
                self.vehicle_id.priority_of_chequed_request = 'normal'
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
        self.tae_stamp = False

    @api.one
    @api.constrains('delivery_date')
    def check_delivery_date(self):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        delivery_date = pytz.utc.localize(datetime.datetime.strptime(self.delivery_date, '%Y-%m-%d %H:%M:%S')).astimezone(local).strftime('%Y-%m-%d')
        now_date = pytz.utc.localize(datetime.datetime.now()).astimezone(local).strftime('%Y-%m-%d')
        
        if  delivery_date < now_date :
            raise ValidationError("La fecha de programacion no puede ser en el pasado")

    @api.constrains('delivery_date')
    def set_reprogrammed(self):
        if (self.delivery_date != self.olddate) and (self.olddate is not False):
            self.state = 'reprogrammed'
        self.olddate = self.delivery_date
        self.vehicle_id.priority_of_chequed_request = 'normal'
        self.client_arrival = False
        self.tae_stamp = False

    @api.one
    def stamp_tae(self):
        if not self.tae_stamp:
            self.tae_stamp = fields.Datetime.now()
        

    @api.one
    @api.constrains('vehicle_id')
    def chek_vehicle_ready_for_delivery(self):
        if bool(self.vehicle_id):
            result_search = self.env['delsol.delivery'].search([('vehicle_id','=',self.vehicle_id.id)])
            if len(result_search)>1:
                msg = "El vehiculo ya fue entregado/despachado"
                if (result_search[0].state == 'new')|(result_search[0].state == 'reprogrammed'):
                   msg = "La entrega ya esta programada." 
                raise ValidationError(msg)
                return
            if (self.vehicle_id.state not in ("to_be_delivery","ready_for_delivery")):
                if ((self.vehicle_id.state  in ('damage')) & self.env.user.has_group('entregas.group_name_admin_entregas_damaged')):
                    self.env.user.notify_warning("El vehiculo se encuentra dañado!!.")                        
                else:
                    raise ValidationError("El vehiculo no esta listo para programar la entrega.")
                    return


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
    
    
    def _client_vehicle_readonly(self):
        
        if ((self.state == 'delivered') |
            (self.vehicle_id.state == 'to_be_delivery') |
            (self.vehicle_id.state == 'ready_for_delivery') |
            (self.vehicle_id.state == 'damage')):
            self.client_vehicle_readonly = True
        else:
            self.client_vehicle_readonly = False

    
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
                cliente = record.client_id.name_get_str(record.client_id) or ''
            
            if record.delivery_date:
                fecha = str(record.delivery_date[0:10])
            
            if record.vehicle_id:
                vehiculo = str(record.vehicle_id.name_get_str(record.vehicle_id)) or ''

            return cliente + '(' + str(vehiculo) + '), ' + fecha  
        

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
            
            #r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS=" +smsnro + "&TEXTO=" + smstexto + "&USUARIO=" + smsuser + "&CLAVE=" + smsclave)
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
            
            
            smstexto = "Del sol le da la bienvenida y le desea muchas felicidades. La clave de la wifi DEL SOL CLIENTES es delsolautomotor"
            #"llego el cliente " + cliente_id.nombre
            
            #r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS=" +smsnro + "&TEXTO=" + smstexto + "&USUARIO=" + smsuser + "&CLAVE=" + smsclave)    
            print 'r = requests.get("http://servicio.smsmasivos.com.ar/enviar_sms.asp?API=1&TOS="' +smsnro + '&TEXTO=' + smstexto + '&USUARIO=' + smsuser + '&CLAVE=' + smsclave +")"

            print r.status_code
            print r.headers
            print r.content
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
        