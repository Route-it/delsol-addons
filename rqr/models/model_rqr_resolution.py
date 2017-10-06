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

class delsol_rqr_resolution(models.Model):
    
    _name = "delsol.rqr_resolution"
     
    rqr_id = fields.Many2one("delsol.rqr",required=True)

    name = fields.Text("Accion",required=True)
    comentario_resolucion = fields.Text("Comentarios")

    date_start = fields.Date("Fecha inicio",readonly=True,invisible=True)
    date_end = fields.Date("Fecha fin",readonly=True,invisible=True)


    #Sirve para modificar los valores por defecto de la vista
    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(delsol_rqr_resolution, self).default_get(fields)

        if ('rqr_id' in fields) & bool(context.get('rqr_id')):
            res.update({'rqr_id': context.get('rqr_id')})
        
        return res

