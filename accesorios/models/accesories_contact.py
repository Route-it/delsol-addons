# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import date, datetime

import datetime
from openerp.exceptions import ValidationError, Warning
import pytz

class accesories_contact(models.Model):
    _name = 'delsol.accesories_contact'

    state = fields.Selection([('contacted','Contactado'),('not_contacted','No Contactado'),('call_back','Volver a llamar')],"Estado de contacto",default='call_back')
    accesories_ids = fields.Many2many(comodel_name="delsol.accesories",relation="delsol_accesories_contact_accesories"
                                      ,column1="accesories_contact_id",column2="accesories_id"
                                      ,string="Accesorios solicitados")
    accesories_request = fields.Boolean("Desea accesorios?",default=False)

    create_date = fields.Datetime("Fecha de contacto",readonly=True)

    state_install = fields.Selection([('colocado','Colocado'),('en_curso','En Curso'),('no_colocado','No Colocado')],"Estado de instalacion",default='no_colocado')

    init_install_date = fields.Datetime("Inicio de instalacion",readonly=True,default=False) 
    end_install_date = fields.Datetime("Fin de instalacion",readonly=True,default=False)
    button_end_install_date_visible = fields.Boolean(compute="_compute_end_install_date_visible")

    programmed_install_date = fields.Datetime("Fecha de programacion de instalacion")

    priority = fields.Selection("Prioridad",related="vehicle_id.priority_of_chequed_request",readonly=True,store=True)
    
    install_duration = fields.Integer(default=60,readonly=True,store=False)
    
    notify_email_send_date = fields.Datetime("Fecha de aviso a responsable",readonly=True)
    
    annotations = fields.Text("Anotaciones")

    vehicle_id = fields.Many2one("delsol.vehicle",string="Vehiculo",required=True)
    vehicle_model_id = fields.Many2one("delsol.vehicle_model",related="vehicle_id.modelo",help="Para filtrar accesorios por modelo", readonly=True)

    client_id = fields.Many2one("res.partner",related="vehicle_id.client_id",string="Cliente", readonly=True)

    #client_phone = fields.Char("Telefono",computed="_get_telefono_cliente", readonly=True)
    client_phone = fields.Char("Telefono",related="client_id.phone", readonly=True)
    client_mobile = fields.Char("Movil",related="client_id.mobile", readonly=True)

    delivery_date = fields.Datetime("Fecha de entrega",related="vehicle_id.delivery_id.delivery_date", readonly=True,store=True)
    sector = fields.Selection(related="vehicle_id.delivery_id.sector", readonly=True)
    
    @api.one
    def _compute_end_install_date_visible(self):
        self.button_end_install_date_visible = (not bool(self.end_install_date)) & bool(self.init_install_date)  
        return self.button_end_install_date_visible
    
    
    @api.onchange('state')
    def onchange_state(self):
        if self.state == 'not_contacted':
            self.accesories_request = False
            
    
    @api.one
    @api.constrains('programmed_install_date')
    def validate_client(self):
        if not bool(self.client_id):
            raise ValidationError("No hay cliente asignado. No se puede contactar.")
            return
        
        if (not bool(self.client_phone)) & (not bool(self.client_mobile)):
            self.env.user.notify_warning("El cliente no tiene telefonos cargados. No se puede contactar.")
            return

        
        
    @api.one
    @api.constrains('programmed_install_date')
    def validate_programmed_install_date(self):
        
        if (self.state == 'not_contacted'): return
        if (self.state == 'call_back'): return
        
        if not bool(self.programmed_install_date): return
            #self.programmed_install_date = datetime.datetime.now()

        date_v_created = self.vehicle_id.create_date

        if self.programmed_install_date < date_v_created:
                    self.env.user.notify_warning("La fecha de instalacion de accesorios no puede ser anterior al ingreso del vehiculo al sistema.")
                    raise ValidationError("La fecha de instalacion de accesorios no puede ser anterior al ingreso del vehiculo al sistema.")
                    return

        if bool(self.create_date):
            date_contact_created = self.create_date

            if self.programmed_install_date < date_contact_created:
                        self.env.user.notify_warning("La fecha de instalacion de accesorios no puede ser anterior al contacto para su venta.")
                        raise ValidationError("La fecha de instalacion de accesorios no puede ser anterior al contacto para su venta.")
                        return
             
        if bool(self.vehicle_id.delivery_id):
            date_delivery = self.vehicle_id.delivery_id.delivery_date
        
            if self.programmed_install_date > date_delivery:
                        self.env.user.notify_warning("La fecha de instalacion de accesorios esta luego de la fecha de entrega del vehiculo.")
                        #raise ValidationError("La fecha de instalacion de accesorios esta luego de la fecha de entrega del vehiculo.")
                        return
        
        return

    """
    Reglas:
    1) Si estado es no contactado, se deben eliminar los accesorios agregados. e inhabilitar la parte de instalacion
    2) Si estado es contactado. Habilitar la parte de instalacion
    
    3) La fecha de programacion de instalacion, debe ser sugerida por el sistema.
       Validacion:
       a) posterior a la fecha de creacion del vehiculo
       b) posterios a la fecha de carga del registro de contacto
       c) advertir si la fecha es mayor que la fecha de entrega.
    
    4) hacer readonly cliente, modelo del vehiculo y estado de instalacion
    5) cargar vehiculo automaticamente si viene del formulario del vehiculo y ponerlo readonly
    
    6) agregar botones de flujo (instalado, contactado, otro.
    """   

    @api.multi
    def init_install(self):
        
        for record in self:
            #user_tz = self.env.user.tz or pytz.utc
            #local = pytz.timezone(user_tz)
            #fecha_hora_local = pytz.utc.localize(datetime.datetime.now()).astimezone(local)            
            record.init_install_date = fields.Datetime.now()
            record.state_install = 'en_curso'
            if not bool(record.programmed_install_date):
                try:
                    record.programmed_install_date = record.init_install_date 
                except:
                    self.env.user.notify_warning("La fecha de instalacion de accesorios no puede ser anterior al contacto para su venta.")
        
        return

    @api.multi
    def end_install(self):
        for record in self:
            #user_tz = self.env.user.tz or pytz.utc
            #local = pytz.timezone(user_tz)
            #fecha_hora_local = pytz.utc.localize(datetime.datetime.now()).astimezone(local)            
            record.end_install_date = fields.Datetime.now()
            record.state_install = 'colocado'
        
        return

    @api.one
    def name_get(self):
        mystate = ''
        for st in self._fields['state'].selection:
            if st[0] == self.state:
                mystate = st[1]
                break
        mystate_install = ''
        for st in self._fields['state_install'].selection:
            if st[0] == self.state_install:
                mystate_install = st[1]
                break
        client_name = 'Sin cliente asignado'
        if bool(self.client_id.name):
            client_name = self.client_id.name
            
        name = client_name +' ('+ mystate +'/'+ mystate_install +')'
        return  (self.id, name)
        
        