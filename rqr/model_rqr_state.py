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

class delsol_rqr_state(models.Model):
    
    _name = "delsol.rqr_state"
     
    _order = 'sequence'
    name = fields.Char('Nombre de la etapa', required=True, translate=True)
    sequence = fields.Integer('Secuencia')
    fold = fields.Boolean('Replegada',
                               help='Esta estapa esta replegada en la vista de kanban cuando no hay'
                               'registros que mostrar.')


