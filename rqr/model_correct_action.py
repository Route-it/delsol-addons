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
     
    rqr_id = fields.Many2one("delsol.rqr",required=True)

    name = fields.Text("Accion",required=True)
    comentario_resolucion = fields.Text("Comentarios")

    date_start = fields.Date("Fecha inicio",readonly=True,invisible=True)
    date_end = fields.Date("Fecha fin",readonly=True,invisible=True)
