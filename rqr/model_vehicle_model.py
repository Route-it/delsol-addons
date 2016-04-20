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

    name = fields.Char(string="Nombre")
    
    @api.onchange('name')
    def onchange_name(self, cr, uid, ids, name, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if record.name:
                record.name =  str(name).title()


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, self.name_get_str(record)))
        
        return res
    
    def name_get_str(self,record):
        res = record.name or ''
        return res.encode('utf8')    

