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

class delsol_vehicle_model(models.Model):
    
    _name = "delsol.vehicle_model"

    name = fields.Char(string="Código de catálogo",required=True)
    
    description = fields.Char(string="Descripción")
    
    turn_duration = fields.Integer("Tiempo de entrega",help="Tiempo en minutos de duración de turno",default=60)
    

    _sql_constraints = [
            ('vehicle_model_name_unique', 'unique(name)', 'El código debe ser único'),
    ]
    
    @api.onchange('name')
    def onchange_name(self):      
        if self.name:
            self.name =  str(self.name).upper()

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, self.name_get_str(record)))
        return res
    
    def name_get_str(self,record):
        return_value = ''
        return_value += record.description or ""
        return_value += '('
        return_value += record.name
        return_value += ')'
        return return_value.encode('utf8')    
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('description', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

