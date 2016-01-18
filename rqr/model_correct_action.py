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

class delsol_correct_action(models.Model):
    
    _name = "delsol.correct_action"
     
    name = fields.Text("Accion",required=True)

    rqr_id = fields.Many2one("delsol.rqr",required=True)

    date_start = fields.Date("Fecha inicio",readonly=True)
    date_end = fields.Date("Fecha fin",readonly=True)
    comentario_resolucion = fields.Text("Comentarios")

