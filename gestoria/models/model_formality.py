# -*- coding: utf-8 -*-

from datetime import datetime

from openerp import models, fields, api
from openerp.exceptions import ValidationError
import pytz


class delsol_formality(models.Model):
    _name = 'delsol.formality'
    
    _inherit = ["mail.thread", "ir.needaction_mixin"]
    
    _order = "create_date asc"

    FORMALITY_STATE = [('new', 'Nuevo'),
                       ('initiated', 'Iniciado'),
                       ('observed', 'Observado'),
                       ('delayed', 'Demorado'),
                       ('completed', 'Completado'),
                       ('finalized', 'Finalizado'),
                       ]

    name = fields.Char('Nombre')
    # fecha Pase a gestoria create date?
    create_date = fields.Datetime("Fecha de pase a gestoria", readonly=True)
    folder_sign_send_date = fields.Datetime("Fecha de envio de carpeta para firma", readonly=True,default=False)
    folder_sign_receiv_date = fields.Datetime("Fecha de recibo de carpeta firmada", readonly=True,default=False)
     
    def _get_responsible_domain(self):
        
        hr_empl = self.env['hr.employee'].search([('department_id.name','ilike','gestor'),('active','=',True)])
        
        responsibles = hr_empl.mapped('user_id.id')
                    
        return [('id', 'in', responsibles)]
    
    formality_responsible_id = fields.Many2one('res.users', string='Responsable', track_visibility='onchange'
                                               ,domain=_get_responsible_domain,
                                               help="El responsable tiene que estar como empleado en el Departamento de Gestoria, y ser usuario del sistema")
    
    fomarlity_gestor_id = fields.Many2one('res.partner', string='Gestor', track_visibility='onchange') 

    formality_type_ids = fields.Many2many(comodel_name="delsol.formality_type",
                                          relation="delsol_formality_formality_type",
                                          column1="formality_id",column2="formality_type_id",
                                          string="Formularios", required=True, track_visibility='onchange')

    # Requisitos --> a relevar.    

    # cuando el tramite se inica?
    formality_in_registry_date = fields.Datetime("Fecha ingreso a registro", help="Fecha que el tramite ingreso al registro", track_visibility='onchange')
    
    # Si tramite es 01:    
    patent_date = fields.Datetime("Fecha de patentamiento", track_visibility='onchange')
    
    patent = fields.Char(related="vehicle_id.patente", track_visibility='onchange')    

    nro_chasis = fields.Char(related="vehicle_id.nro_chasis", readonly=True)    

    vehicle_registry_id = fields.Many2one('delsol.vehicle_registry', string="Registro", track_visibility='onchange')

    registry_by_address = fields.Text(string="Consultar registro por direccion",compute="_registry_by_address")

    papers_received_date = fields.Datetime("Fecha de recibo de papeles", readonly=True, track_visibility='onchange')
    formality_complete_date = fields.Datetime("Fecha de finalizacion de tramite", readonly=True, track_visibility='onchange')
    title_received_date = fields.Datetime("Fecha de recibo de titulo", readonly=True, track_visibility='onchange')
    
    # Enviar un sms al cliente cuando se carga este campo?
    fordward_sales_admin_date = fields.Datetime("Fecha de pase a ventas", readonly=True, track_visibility='onchange')
    
    state = fields.Selection(FORMALITY_STATE, default="new", string="Estado del tramite", required=True, track_visibility='onchange')

    # Fecha Pase Carpeta a Admin Ventas --> estado de tramite finalizado
    
    title_delivery_to_client_date = fields.Datetime("Entrega de titulo", help="Fecha de entrega de titulo al cliente", readonly=True, track_visibility='onchange')

    comments = fields.Text("Anotaciones")

    vehicle_id = fields.Many2one('delsol.vehicle', string="Vehiculo", help="Vehiculo", required=True, track_visibility='onchange')

    client_id = fields.Many2one(related='vehicle_id.client_id', string="Cliente", required=True, readonly=True, track_visibility='onchange')

    client_address = fields.Char(compute='_compute_address', string="Direccion del Cliente", readonly=True)

    # Se calcula cuando se finaliza el tramite.
    time_delayed_in_formality = fields.Integer("Demora (Dias)", readonly=True, compute="_delayed_time") 

    @api.onchange('vehicle_id')
    def change_vehicle(self):
        if bool(self.vehicle_id.patente):
            self.env.user.notify_info('El vehiculo seleccionado ya esta patentado.')

    @api.one
    @api.depends('client_id')
    def _compute_address(self):
        street = self.client_id.street if bool(self.client_id.street) else ''
        street2 = self.client_id.street2 if bool(self.client_id.street2) else ''
        
        address = street + ' ' + street2
        if len(address)>1:
            self.client_address = address  
        else:
            self.client_address =  'El cliente no tiene direccion cargada.'

    @api.one
    def _registry_by_address(self):
        link = self.env['delsol.config'].search([('code','=','gestoria_link_reg_by_address')])
        if len(link)>0:
            self.registry_by_address = link[0].value
        
        #    <record id="gestoria_link_reg_by_address" model="delsol.config">
        #    <field name="name">Registro por direccion</field>
        #    <field name="code">gestoria_link_reg_by_address</field>

    @api.onchange('patent')
    @api.one
    def onchange_patente(self):
        if self.patent:
            self.patent = str(self.patent).upper()
        
        
    @api.one
    def _delayed_time(self):
        aux = datetime.utcnow()
        if bool(self.fordward_sales_admin_date):
            aux = datetime.strptime(self.fordward_sales_admin_date ,"%Y-%m-%d %H:%M:%S")
        self.time_delayed_in_formality = (aux - datetime.strptime(self.create_date,"%Y-%m-%d %H:%M:%S")).days
        

    @api.one
    def name_get(self):
        nom = ''
        vehi = ''
        state = ''
        reg = ''
        if self.client_id:
            nom = self.client_id.name or ''
        if self.vehicle_id:
            vehi = self.vehicle_id.nro_chasis or ''
        state = self.state or ''
        if self.vehicle_registry_id:
            reg = (' - ' + self.vehicle_registry_id.name_get()[0][1])or ''
        return (self.id, nom + ' / ' + vehi + ' (' + state + ') ' + reg)
        

    @api.multi
    def set_go_gerencia(self):
        
        for i in self:
            if not bool(i.folder_sign_receiv_date):
                i.folder_sign_send_date = datetime.now()
    
    @api.multi
    def set_back_gerencia(self):

        for i in self:
            if not bool(i.folder_sign_receiv_date):
                i.folder_sign_receiv_date = datetime.now()
        
    @api.multi
    def set_initiated(self):
        for i in self:
            if (not bool(i.folder_sign_receiv_date)): 
                self.env.user.notify_info('Debe firmarse primero la carpeta.')
                return 
            if (not bool(i.vehicle_registry_id)):
                self.env.user.notify_info('Debe asignar un registro.')
                return 
            if (not bool(i.formality_responsible_id)):
                self.env.user.notify_info('Debe asignar un responsable del tramite')
                return 
            i.state = 'initiated'

            i.formality_in_registry_date = datetime.now()

    @api.multi
    def set_observed(self):
        for i in self:
            i.state = 'observed'
            if bool(i.comments):
                i.comments = i.comments +  '\n Tramite Observado'
            else: 
                i.comments = 'Tramite Observado'

    @api.multi
    def set_delayed(self):
        for i in self:
            i.state = 'delayed'
    @api.multi
    def set_completed(self):
        for i in self:
            if ((not bool(i.patent_date)) | (not bool(i.patent))):
                self.env.user.notify_info('Debe completarse la patente y la fecha de patentamiento primero.')
                return

            i.state = 'completed'

            i.papers_received_date = datetime.now()
            i.fordward_sales_admin_date = datetime.now() 
            i.formality_complete_date = datetime.now()
    
    @api.multi
    def set_title_recived(self):

        for i in self:
            i.title_received_date = datetime.now()

            
    @api.multi
    def set_finalized(self):

        for i in self:
            i.state = 'finalized'
            i.title_delivery_to_client_date = datetime.now()
            