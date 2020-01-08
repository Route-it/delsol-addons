# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from time import time
from datetime import datetime
from lxml import etree

class delsol_rqr(models.Model):
    _name = 'delsol.service'

    _inherit = ["mail.thread", "ir.needaction_mixin"]
    
    
    client_id = fields.Many2one(related='vehicle_id.client_id',string="Cliente",required=True,readonly=True,
                                track_visibility='onchange')

    vehicle_id = fields.Many2one('delsol.vehicle',string="Vehiculo", help = "Vehiculo",required=True,track_visibility='onchange',
                                 domain=_vehicle_id_domain)


    turn_date = fields.Datetime("Fecha y hora del turno")
    delivery_date = fields.Datetime("Fecha y hora de entrega")
    order_date = fields.Datetime("Fecha y hora de orden")
    
    #BZ, EM, MN, MS, S.G., SUG, RQR 
    status = fields.Selection([('bz', 'Muy Satisfactorio'),('em','Satisfactorio')
                               ,('mn','RQR')
                               ,('ms','RQR')
                               ,('sg','RQR')
                               ,('sug','RQR')
                               ,('rqr','RQR')
                               ],"Estado")

    #flotas es status
    cvp = fields.Boolean("CVP")    
    cc = fields.Selection([('sii', 'Si+')
                           ,('si','Si')
                               ,('no','No')
                               ],"CC") 
    asesor = fields.Many2one("hr.employee",String="Asesor")
  
    phone = fields.Char(string="Telefono",related="delivery_id.client_id.phone",readonly=True)
    mobile = fields.Char(string="Movil",related="delivery_id.client_id.mobile",readonly=True)
    email = fields.Char(string="Mail",related="delivery_id.client_id.email",readonly=True)

    vehicle_model = fields.Many2one(related='vehicle_id.modelo',string="Modelo del vehiculo",readonly=True)    
    vehicle_patent = fields.Many2one(related='vehicle_id.modelo',string="Modelo del vehiculo",readonly=True)
    patente = fields.Char(related='vehicle_id.patente',string ="Patente")
    
    asesor = fields.Many2one("hr.employee",String="Mecanico")
    
    odometro = fields.Integer("Odometro")
         
    vehicle_return = fields.Boolean("Retorno")    

    comments = fields.Text("Comentarios")
    
    coming_reason = fields.Text("Comentarios")    


    #delsol call
    
    Responsable del Contacto    
    F. Enviar correo al área    
    Fecha de llamado   
    # puntuacion 
        Asesor de Servicio 
        Calidad de trabajo    
        Proceso de entrega    
        Cumplir los acuerdos establecidos    
        Adorar concesionario    
        OK    
    cantidad de llamadas = ?    

    Voz del Cliente = 1 voz por cada llamada   
    
    TIPO DE RQR = queja, reclamo, retorno, garantia, sugerencia 
    CATEGORIA DE RQR = repuesto pendiente, explicacion asesor, mal lavado, 
                    tiempo entrega, precio,    
    STATUS DE RQR = nuevo, en curso, resuelto, cerrado
    PROCESO DE RESOLUCIÓN 

PUNTAJE CVP    
COMENTARIO CVP


    #Sirve para modificar la vista
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(delsol_rqr, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        context = self._context or {}

        if bool(view_type) & (view_type == 'form') & bool(context.get('delivery_id')):

            for field in res['fields']:
                if field == 'service_id':
                    res['fields'][field]['readonly'] = True
        return res

    
    @api.depends('service_id','tipo_rqr','state')
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            record.name = self.name_get_str(record)
            res.append((record.id, self.name_get_str(record)))
        return res

    
    def name_get_str(self, record):
            service = ''
            tipo_rqr = ''
            state = ''
            if record.service_id:
                service =  record.service_id.name_get_str(record.service_id)
            
            if record.tipo_rqr:
                tipo_rqr =  record.tipo_rqr.name_get_str(record.tipo_rqr)
            if record.state:
                #state =  str(record.state.name_get_str(record.state))
                tempstate = record.state or ''
                state =  tempstate
                
            
            return service +', '+tipo_rqr + ' ('+state+')'
