
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

class config(models.Model):
    
    _name = 'delsol.config'
    
    name = fields.Text('Nombre')
    code = fields.Text('Codigo')
    app = fields.Text('Aplicacion')
    description = fields.Text('Descripcion')
    value = fields.Char('Valor')

    
    