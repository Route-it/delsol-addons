# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from time import time
from datetime import datetime

class delsol_rqr_servicio(models.Model):
    _name = 'delsol.rqr_servicio'

    _inherit = ["mail.thread", "ir.needaction_mixin", "delsol.rqr"]
    
    
    service_id = fields.Many2one("delsol.service", String="Entrega relacionada")
    



CLIENTE     
Fecha del Turno     
Fecha de entrega    
Fecha de OR.     
Status    
flotas     
cvp    
CC    
ASESOR    
Teléfonos    
E-Mail    
Modelo    
MECÁNICO    
PATENTE    
KILOMETRAJE    
RETORNO    
Comentario de Asesor de Servicio / motivo para seguir al cliente     
Motivo de la Visita    
Responsable del Contacto    
F. Enviar correo al área    
Fecha de llamado    
Asesor de Servicio    
Calidad de trabajo    
Proceso de entrega    
Cumplir los acuerdos establecidos    
Adorar concesionario    
OK    
cantidad de llamadas    
Voz del Cliente    
TIPO DE RQR    
CATEGORIA DE RQR    
STATUS DE RQR    
PROCESO DE RESOLUCIÓN.    
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
