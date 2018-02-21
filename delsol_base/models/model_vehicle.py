# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from datetime import date, datetime
import pytz



class delsol_vehicle(models.Model):
    _name = 'delsol.vehicle'

    _inherit = ["mail.thread", "ir.needaction_mixin"]
    
    def _get_states(self):
        return [("new", "Nueva"),
                               ("not_chequed", "Unidad A Chequear"),
                               ("ready_for_programmed", "Lista Para Programar"),
                               ("damage", "Unidad Averiada"),
                               ("repaired_damage", "Unidad Reparada"),
                               ("missing", "Unidad Faltante"),
                               ("to_be_delivery", "A Preparar"),
                               ("ready_for_delivery", "Lista para entregar"),
                               ("dispatched", "Despachado"),
                               ("delivered", "Entregado")
                               ]


    PRIORITY = [("normal", "Normal"),
                               ("high", "Alta")]
    
    
    create_date = fields.Datetime("Fecha de carga", readonly=True)


    client_id = fields.Many2one('res.partner', string="Cliente", domain=[('customer', '=', 'True')], help="Cliente asociado al vehiculo",
                                track_visibility='onchange')


    name = fields.Char(compute="compute_name", store=True, readonly=True)

    marca = fields.Char(string="Marca")
    modelo = fields.Many2one("delsol.vehicle_model", string="Modelo", track_visibility='onchange')
    vehicle_type = fields.Selection(related='modelo.vehicle_type')
    turn_duration = fields.Integer(compute="_turn_duration")    

    color = fields.Many2one("delsol.vehicle_color", string="Color de vehículo", required=True, track_visibility='onchange')
    nro_chasis = fields.Char(string="Nro de Chasis", track_visibility='onchange', required=True)

    fabricante_origen_anio = fields.Char(string="Fabricante/Origen/Año", readonly=True, compute="_compute_vin", help='Datos segun nro de chasis')
    
    serie_vin = fields.Char(string="Serie/Vin", readonly=True, compute="_compute_vin")

    # cambiar por many2one a una entidad que se llame ubicacion
    ubicacion = fields.Char(string="Ubicacion")

    fecha_facturacion = fields.Datetime("Fecha de facturacion")

    date_for_calendar = fields.Datetime(readonly=True)

    state = fields.Selection(_get_states, default="new",
                              string="Estado", required=True, readonly=True)

    priority_of_chequed_request = fields.Selection(PRIORITY, default="normal", string="Prioridad", required=True)

    
    state_list = fields.One2many("delsol.vehicle_status", "vehicle_id", "Estados", ondelete='cascade')

    last_date_of_change_status = fields.Datetime("Utlimo cambio de estado", compute="_compute_last_change_status_date")

    # Fecha Arribo al concecionario -> por lista de estados?

    arrival_to_dealer_date = fields.Datetime(readonly=True)

    pass_predelivery_proccess = fields.Boolean("Saltear proceso de preentrega", track_visibility='onchange', default=False)
    
    
    """logistica    
    factory_payment_date = fields.Datetime("Fecha de pago a fabrica")
    factory_certificate_date =fields.Datetime("Fecha de certificado de fabrica")
    factory_invoice_number = fields.Char("Factura de Fabrica")
    factory_certificate_number = fields.Char("Certificado de Fabrica")
    """


    anios = {
              'A':'2009',
              'B':'2010',
              'C':'2011',
              'D':'2012',
              'E':'2013',
              'F':'2014',
              'G':'2015',
              'H':'2016',
              'I':'2017',
              'J':'2018',
              'K':'2019',
              'L':'2020',
              'M':'2021',
              'N':'2022',
              'P':'2023',
              'R':'2024',
              'S':'2025',
              'T':'2026',
              'V':'2027',
              'W':'2028',
              'X':'2029',
              'Y':'2030',
              '1':'2031',
              '2':'2032',
              '3':'2033',
              '4':'2034',
              '5':'2035',
              '6':'2036',
              '7':'2037',
              '8':'2038',
              '9':'2039',
              }
    
    origenes = {'1':'EEUU',
               '4':'EEUU',
               '5':'EEUU',
               '2':'Canada',
               '3':'Mexico',
               'A':'Sudafrica',
               'J':'Japon',
               'K':'Corea del Sur',
               'L':'China',
               'M':'India-Indonesia-Tailandia',
               'P':'Filipinas-Malasia',
               'S':'Reino Unido-Alemania-Polonia',
               'T':'Suiza-Rep.Checa-Ungria',
               'V':'Austria-Francia-España',
               'X':'Rusia',
               'W':'Alemania',
               'Y':'Belgica-Finlandia-Suecia',
               'Z':'Italia',
               '6':'Australia',
               '7':'Nueva Zelanda',
               '8':'Arg-Chi-Ven',
               '9':'Bra-Col',
               }

    fabricantes = {
              'A':'Audi-Jaguar',
              'B':'BMW-Dodge',
              'F':'Ford-Renault-Citroen',
              'C':'Chevrolet-Chrysler',
              '7':'GM',
              'G':'GM',
              'n':'Honda',
              'D':'Mercedes',
              'N':'Nisan',
              'S':'Saab',
              'T':'Toyota',
              'V':'Volkswagen',
             }

    modelos = {
               '6P8CF':'Mustang',
               'ZH55K':'Ka',
               'ZH54K':'Ka',
               'Z55A9':'Ka',
               'ZH55K':'Ka',
               
               'BZZFH':'Focus',
               'BZZFF':'Focus',
               'NZZFH':'Focus',

               'ZD55N':'Fiesta',
               'FP4WJ':'Fiesta',
               'DP4YJ':'Fiesta',
               'DP4ZJ':'Fiesta',

               'ZB55N':'Ecosport',
               'ZB55U':'Ecosport',

               'AR22K':'Ranger',
               'AR22W':'Ranger',

               '6P0H9':'Mondeo',

               'ADAWP':'Kuga',

               'YEA8E':'Cargo',
               'YEAHD':'Cargo',
               'YEAKD':'Cargo',
               'YEAXV':'Cargo',
               'YEB2B':'Cargo',
               'YEB2B':'Cargo',
               'YEB5J':'Cargo',
               'VEADS':'Cargo',

               'LF49P':'4000',
                       
               }
        
    @api.onchange('nro_chasis')
    def upper_chasis(self):
        if self.nro_chasis:
            self.nro_chasis = str(self.nro_chasis).upper()
        
    _sql_constraints = [
            ('vehicle_chasis_unique', 'unique(nro_chasis)', 'El chasis ya existe'),
    ]

    @api.constrains('nro_chasis')
    def check_chasis(self):
        chasis_corto = self.nro_chasis[-8:]
        vehicles = self.env['delsol.vehicle'].search([('nro_chasis', 'ilike', chasis_corto)])
        if len(vehicles) > 1:
            raise ValidationError("El nro de chasis ya existe. Utilice los ultimos 8 digitos para buscarlo")
            return false

        check_chasis_b = True
        
        try:
            check_chasis = self.env['delsol.config'].search([('code','=','check_nro_chasis')]).value
            check_chasis_b = eval(check_chasis.capitalize()) 
        except:
            check_chasis_b = True
        
        if check_chasis_b:
        
            if not (len(self.nro_chasis) == 17):
                raise ValidationError("El nro de chasis debe tener 17 digitos.")
                return false
            
            valid_chasis = True
            
            if not (self.nro_chasis[:1] in self.origenes):
                valid_chasis = False
            if 'W' == self.nro_chasis[:1]:
                if not (self.nro_chasis[1:2] in self.fabricantes):
                    valid_chasis = False
            else:
                if not (self.nro_chasis[9:10] in self.anios):
                    valid_chasis = False
                if not (self.nro_chasis[2:3] in self.fabricantes):
                    valid_chasis = False
        
            if (not valid_chasis):
                raise ValidationError("El nro de chasis es invalido.")
                return false

    @api.model
    def create(self, vals):
        if bool(vals.get('pass_predelivery_proccess')):
            vals['state'] = 'ready_for_delivery'
        vehicle = super(delsol_vehicle, self).create(vals)
        return vehicle

    @api.multi
    def write(self, vals):
        if bool(vals.get('pass_predelivery_proccess')):
            vals['state'] = 'ready_for_delivery'
        vehicle = super(delsol_vehicle, self).write(vals)
        return vehicle

    @api.one
    def change_state(self, new_state):
        vehicle_status_obj = self.env['delsol.vehicle_status']
        defaults = {'vehicle_id': self.id, 'status':new_state.new_state, 'date_status':new_state.change_state_date, 'user_id':new_state.user_id.id,
                    'comments':new_state.reason, 'priority_of_chequed_request':self.priority_of_chequed_request}
        target_vs = vehicle_status_obj.create(defaults)

        self.state = new_state.new_state
        if new_state.new_state == 'not_chequed' or new_state.new_state == 'to_be_delivery':
            self.date_for_calendar = fields.Datetime.now()
        else:
            self.date_for_calendar = False
            
    



    @api.one
    def _compute_last_change_status_date(self):
        last_status = self.env['delsol.vehicle_status'].search([('vehicle_id', '=', self.id)], order='date_status desc', limit=1)
        if (last_status):
            self.last_date_of_change_status = last_status.date_status



    @api.depends('nro_chasis')
    @api.one
    def _compute_vin(self):
        origen = 'Desconocido'
        anio = 'Desconocido'
        fabricante = 'Desconocida'
        modelo = ''
        if bool(self.nro_chasis):
            self.serie_vin = self.nro_chasis[-8:]


            if (len(self.nro_chasis) == 17):
                if self.nro_chasis[:1] in self.origenes:
                    origen = self.origenes[self.nro_chasis[:1]]
                if 'W' == self.nro_chasis[:1]:
                    if self.nro_chasis[1:2] in self.fabricantes:
                        fabricante = self.fabricantes[self.nro_chasis[1:2]]
                else:
                    if self.nro_chasis[2:3] in self.fabricantes:
                        fabricante = self.fabricantes[self.nro_chasis[2:3]]
                    if self.nro_chasis[9:10] in self.anios:
                        anio = self.anios[self.nro_chasis[9:10]]

                if self.nro_chasis[3:8] in self.modelos:
                    modelo = '/' + self.modelos[self.nro_chasis[3:8]]

        self.fabricante_origen_anio = str(fabricante) + '/' + str(origen) + '/' + str(anio) + str(modelo)
        
        #Mustang
        #1F A 6P8CF 5 H5251136
        
        #Ej chasis: ARG  FORD  
        #            8A   F     AR22K 7    JJ063041
            

    @api.one
    def _turn_duration(self):
        self.modelo.turn_duration / 60

    def _update_status_list(self):
        vehicle_status_obj = self.env['delsol.vehicle_status']
        date_status = fields.Datetime.to_string(datetime.now(pytz.utc))
        defaults = {'vehicle_id': self.id, 'status':self.state, 'date_status':date_status, 'user_id':self.env.user.id,
                    'comments':'', 'priority_of_chequed_request':self.priority_of_chequed_request}
        target_vs = vehicle_status_obj.create(defaults)


    @api.multi
    def button_new_delivery(self):
        if (not bool(self.client_id)) or (self.client_id == False):
            self.env.user.notify_info('La entrega no puede ser creada. Falta definir el cliente.')
            return
        # este es diferente porque en delivery esta el metodo default_get definido.
        context = {'vehicle_id':self.id}
        if (self.pass_predelivery_proccess):
            context['default_delivery_date'] = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')
            context['default_client_date'] = datetime.now(pytz.utc).strftime('%Y-%m-%d %H:%M:%S')

        
        return {
            'name': 'Entrega',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'delsol.delivery',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context,
            # 'domain': [('id', 'in', [x.id for x in self.invoice_ids])],
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
        
        # buscar si el vehiculo esta entregado/despachado. En tal caso, pasarlo a entregado
        
        result_search = self.env['delsol.delivery'].search([('vehicle_id', '=', self.id)])
        
        if len(result_search) > 0:
            if (result_search[0].state == "delivered"):
                self.state = 'delivered'
            if (result_search[0].state == "dispatched"):
                self.state = 'dispatched'
            if (result_search[0].state == "new") | (result_search[0].state == "reprogrammed"):
                self.state = 'repaired_damage'
        else:
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

   
    
    anio = fields.Selection([('2014', '2014'),
                             ('2015', '2015'),
                             ('2016', '2016'),
                             ('2017', '2017'),
                             ('2018', '2018')],
                             'Modelo Año', required=True, copy=False, default="2017")
    
    _defaults = {
        'marca': 'Ford'
    }
    
    
    @api.depends('marca', 'modelo', 'anio')
    @api.multi
    def compute_name(self):
        for vehi in self:
            vehi.name = vehi.name_get_str(vehi)

    def name_get_str(self, record):
            marca = ''
            modelo = ''
            chasis = ''
            year = ''
            
            if record.anio:
                # year = self.anio[0:4] usado en caso de campo tipo date.
                year = record.anio
    
            if record.marca:
                marca = record.marca or ''
            if record.modelo:
                modelo = record.modelo.name_get_str(record.modelo) or ''
            if record.nro_chasis:
                chasis = record.nro_chasis or ''
            # if record.patente:
            #    patente = record.patente or ''
        
            return str(marca) + '/' + str(modelo) + ' (' + str(year) + ') ' + str(chasis)  
