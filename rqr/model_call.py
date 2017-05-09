# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
from datetime import date


import logging

_logger = logging.getLogger(__name__)

class delsol_call(models.Model):

    _name = "delsol.call"
    
    name = fields.Char(compute="name_get", store=True, readonly=True)
    
    delivery_id = fields.Many2one("delsol.delivery")
    delivery_state = fields.Selection(string="Estado de entrega",related="delivery_id.state",readonly=True)
    
    phone = fields.Char(string="Telefono",related="delivery_id.client_id.phone",readonly=True)
    mobile = fields.Char(string="Movil",related="delivery_id.client_id.mobile",readonly=True)
    email = fields.Char(string="Mail",related="delivery_id.client_id.email",readonly=True)
    
    contact_date = fields.Datetime(string="Fecha de contacto")
    contact_type = fields.Selection([('tel', 'Telefono'),('mail','Correo electronico')],"Tipo de contacto")
    contacted = fields.Boolean(string="Contactado?")
    why_no_contacted = fields.Many2one("delsol.why_no_contacted")
    
    conformity = fields.Selection([('ms', 'Muy Satisfactorio'),('s','Satisfactorio'),('rqr','RQR')],"Nivel de Conformidad")
    
    #esto hay que reemplazarlo
    asesor_ventas = fields.Integer("Asesor de Ventas",default=3)
    experiencia_pago = fields.Integer("Experiencia de pago",default=3)
    cumplimiento = fields.Integer("Cumplimiento de Acuerdos",default=3)
    proceso_entrega = fields.Integer("Proceso de entrega",default=3)

    comment = fields.Text(string="Voz del cliente")
    
    rqr_root_id = fields.Many2one("delsol.rqr", string="RQR", readonly=True)

    resolution_id = fields.Many2one(related="rqr_root_id.resolution_id", string="Resolucion", readonly=True)
    
    
    
    @api.constrains('asesor_ventas','experiencia_pago','cumplimiento','proceso_entrega')
    def check_range(self):
        if bool(self.asesor_ventas):
            if bool(self.asesor_ventas) & (self.asesor_ventas <1 | self.asesor_ventas > 5):
                    raise ValidationError("El campo Asesor de Ventas es incorrecto.")
                    return
        if bool(self.experiencia_pago):
            if bool(self.experiencia_pago) & (self.experiencia_pago <1 | self.experiencia_pago > 5):
                    raise ValidationError("El campo Experiencia de Pago es incorrecto.")
                    return
        if bool(self.cumplimiento):
            if bool(self.cumplimiento) & (self.cumplimiento <1 | self.cumplimiento > 5):
                    raise ValidationError("El campo Cumplimiento es incorrecto.")
                    return
        if bool(self.proceso_entrega):
            if bool(self.proceso_entrega) & (self.proceso_entrega <1 | self.proceso_entrega > 5):
                    raise ValidationError("El campo Proceso de Entrega es incorrecto.")
                    return
        
    @api.constrains('conformity')
    def check_conformity(self):
        if self.conformity=="rqr":
            if self.delivery_id.state != 'delivered':
                raise ValidationError("Conformidad no puede ser RQR si la entrega no esta en estado 'Entregado'")
                return
            
            
            
    #Sirve para modificar los valores por defecto de la vista
    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(delsol_call, self).default_get(fields)

        if ('delivery_id' in fields) & bool(context.get('delivery_id')):
            res.update({'delivery_id': context.get('delivery_id')})
        
        return res

            
            
    def make_rqr(self,cr, uid, ids, context=None):
        rqr_obj = self.pool['delsol.rqr']
        #rqr_state_obj = self.pool['delsol.rqr_state']
        #rqr_state = rqr_state_obj.search(cr, uid, [('sequence','=', 0)])
        
        
        for call in self.browse(cr, uid, ids, context=context):
        #check if delivery is delivered.
            if call.delivery_id.state != 'delivered':
                raise Warning('La entrega debe estar en estado "Entregado".')
                return
            
            message = 'Ya se posee una rqr generada.'
            
            if not bool(call.rqr_root_id):
                defaults = {'delivery_id': call.delivery_id.id,'state':'new','call_root_id':call.id,"sector":call.delivery_id.sector}
                
                target_rqr =  rqr_obj.create(cr, uid, defaults, None)
                
                call.rqr_root_id = target_rqr
                call.conformity = 'rqr'
                message = 'Se genero correctamente la RQR.'


            """
            warning = {
                        'title': 'Mensaje !',
                        'message': message
                     }
            """
            
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
            
    def name_get(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, self.name_get_str(record)))
            
        return res
    
    def name_get_str(self,record):
            entrega = ''
            contactado = ''
                
            if record.delivery_id:
                entrega = str(record.delivery_id.name_get_str(record.delivery_id)) or ''
            
            if record.contacted:
                contactado = "Contactado"
            else:
                contactado = "No Contactado"

            return str(entrega) + '(' + str(contactado) + ')'  
