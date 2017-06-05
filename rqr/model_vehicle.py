# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from datetime import date, datetime
import pytz


class delsol_vehicle(models.Model):
    _name = 'delsol.vehicle'

    _inherit = ["mail.thread", "ir.needaction_mixin"]


    STATES = [("new","Nueva"),
                               ("not_chequed","Unidad A Chequear"),
                               ("ready_for_programmed","Lista Para Programar"),
                               ("damage","Unidad Averiada"),
                               ("repaired_damage","Unidad Reparada"),
                               ("missing","Unidad Faltante"),
                               ("to_be_delivery","A Preparar"),
                               ("ready_for_delivery","Lista para entregar"),
                               ("dispatched","Despachado"),
                               ("delivered","Entregado")
                               ]

    PRIORITY = [("normal","Normal"),
                               ("high","Alta")]
    
    
    create_date = fields.Datetime("Fecha de carga",readonly=True)


    name = fields.Char(compute="compute_name", store=True, readonly=True)

    marca = fields.Char(string ="Marca")
    modelo = fields.Many2one("delsol.vehicle_model",string ="Modelo",track_visibility='onchange')
    vehicle_type = fields.Selection(related='modelo.vehicle_type')
    turn_duration = fields.Integer(compute="_turn_duration")    

    color = fields.Many2one("delsol.vehicle_color",string ="Color de vehículo",required=True,track_visibility='onchange')
    patente = fields.Char(string ="Patente",track_visibility='onchange'
                          ,write=['base.user_root','rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator']
                          )
    nro_chasis = fields.Char(string="Nro de Chasis",track_visibility='onchange')

    
    ubicacion = fields.Char(string="Ubicacion")

    fecha_facturacion = fields.Datetime("Fecha de facturacion")

    date_for_calendar = fields.Datetime(readonly=True)

    state = fields.Selection(STATES,default="new",
                              string="Estado",required=True,readonly=True)

    priority_of_chequed_request = fields.Selection(PRIORITY,default="normal",string="Prioridad",required=True
                                                   ,write=['base.user_root','rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator']
                                                   )

    
    
    state_list = fields.One2many("delsol.vehicle_status","vehicle_id","Estados",ondelete='cascade')


    button_create_delivery_visible = fields.Boolean(compute="_button_create_delivery_visible")    

    @api.multi
    def _button_create_delivery_visible(self):
            self.ensure_one()
            if bool(self.id):
                result_search = self.env['delsol.delivery'].search([('vehicle_id','=',self.id)])
                if len(result_search)>0:
                    self.button_create_delivery_visible = False
                else:
                    if (self.state not in ('ready_for_delivery','to_be_delivery')):
                        self.button_create_delivery_visible = False
                    else:
                        self.button_create_delivery_visible = True
        
        
        
        
    @api.one
    def _turn_duration(self):
        self.modelo.turn_duration/60

    def _update_status_list(self):
        vehicle_status_obj = self.env['delsol.vehicle_status']
        date_status = fields.Datetime.to_string(datetime.now(pytz.utc))
        defaults = {'vehicle_id': self.id,'status':self.state,'date_status':date_status,'user_id':self.env.user.id,
                    'comments':'','priority_of_chequed_request':self.priority_of_chequed_request}
        target_vs =  vehicle_status_obj.create(defaults)


    @api.multi
    def button_new_delivery(self):
        return {
            'name': 'Entrega',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'delsol.delivery',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': {'vehicle_id':self.id},
            #'domain': [('id', 'in', [x.id for x in self.invoice_ids])],
        }


    @api.one
    def state_new(self):
        self.date_for_calendar = False
        self.state = 'new'
        self._update_status_list()
        
    @api.one
    def not_chequed(self):
        self.date_for_calendar = fields.Datetime.now()
        self.state = 'not_chequed'
        self._update_status_list()
       
    @api.one    
    def ready_for_programmed(self):
        self.date_for_calendar = False
        self.state = 'ready_for_programmed'
        self._update_status_list()

    @api.one    
    def damage(self):
        self.date_for_calendar = False
        self.state = 'damage'
        self._update_status_list()

    @api.one    
    def repaired_damage(self):
        self.date_for_calendar = False
        self.state = 'repaired_damage'
        self._update_status_list()

    @api.one    
    def state_missing(self):
        self.date_for_calendar = False
        self.state = 'missing'
        self._update_status_list()

    @api.one    
    def to_be_delivery(self):
        self.date_for_calendar = fields.Datetime.now()
        self.state = 'to_be_delivery'
        self._update_status_list()

    @api.one    
    def ready_for_delivery(self):
        self.date_for_calendar = False
        self.state = 'ready_for_delivery'
        self._update_status_list()

   
    
    anio = fields.Selection([('2014','2014'),
                             ('2015', '2015'),
                             ('2016','2016'),
                             ('2017','2017'),
                             ('2018','2018')],
                             'Modelo Año', required=True, copy=False)
    
    _sql_constraints = [
            ('vehicle_patente_unique', 'unique(patente)', 'La patente ya existe'),
    ]
    
    _defaults = {
        'marca': 'Ford'
    }
    
    
    @api.constrains('patente')
    def check_patente(self):
        for record in self:
            pat = record.patente
            if not bool(pat): return
            anio = record.anio
            if ((len(pat) != 6) and (len(pat) != 7)):
                raise ValidationError("El campo patente debe tener 6 o 7 caracteres.")
                return
            elif (len(pat) == 6) & (int(anio) < 2017) :
                if not pat[3:6].isdigit():
                    raise ValidationError("El campo patente no posee los 3 numeros.")
                    return
                if not pat[0:3].isalpha():
                    raise ValidationError("El campo patente no posee las 3 letras.")
                    return    
            elif (len(pat) == 7) & (int(anio) >= 2016):
                if not pat[0:2].isalpha():
                    raise ValidationError("Los primeros dos dígitos de la patente no son letras")
                    return
                if not pat[2:5].isdigit():
                    raise ValidationError("Los d{igitos 3 4 y 5 deben ser números")
                    return
                if not pat[5:7].isalpha():
                    raise ValidationError("Los últimos dos dígitos deben ser números")
                    return
            # Se quita la obligacion de cargar patente.
            # Revisar en que momento hay que obligar cargarla.
            else: 
                raise ValidationError("La patente es invalida")
                return
                
    @api.onchange('patente')
    def onchange_patente(self):
        if self.patente:
            self.patente = str(self.patente).upper()

    @api.onchange('nro_chasis')
    def onchange_nro_chasis(self):
        if self.nro_chasis:
            self.nro_chasis = str(self.nro_chasis).upper()
    
    @api.depends('marca','modelo','patente','anio')
    @api.multi
    def compute_name(self):
        for vehi in self:
            vehi.name = vehi.name_get_str(vehi)

    def name_get_str(self, record):
            marca = ''
            modelo = ''
            patente = ''
            year = ''
            
            if record.anio:
                #year = self.anio[0:4] usado en caso de campo tipo date.
                year = record.anio
    
            if record.marca:
                marca = record.marca or ''
            if record.modelo:
                modelo = record.modelo.name_get_str(record.modelo) or ''
            if record.patente:
                patente = record.patente or ''
        
            return str(marca.encode('utf8')) + '/' + str(modelo.encode('utf8')) + ' (' +str(year)+') ' + patente  
