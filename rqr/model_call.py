# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class delsol_call(models.Model):
    _name = "delsol.call"
    
    name = fields.Char(compute="name_get", store=True, readonly=True)
    
    delivery_id = fields.Many2one("delsol.delivery")
    
    phone = fields.Char(string="Telefono",related="delivery_id.client_id.phone",readonly=True)
    mobile = fields.Char(string="Movil",related="delivery_id.client_id.mobile",readonly=True)
    email = fields.Char(string="Mail",related="delivery_id.client_id.email",readonly=True)
    
    contact_date = fields.Datetime(string="Fecha de contacto")
    
    contacted = fields.Boolean(string="Contactado?")
    
    why_no_contacted = fields.Many2one("delsol.why_no_contacted")
    
    comment = fields.Text(string="Comentario")
    
    contact_type = fields.Selection([('tel', 'Telefono'),('mail','Correo electronico')],"Tipo de contacto")
    
    _defaults = {
               create_uid: self.env.user 
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
