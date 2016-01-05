
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

class client(models.Model):
    
    inherit = 'res.client'
    
    cuit = fields.Char("CUIT/CUIL", help = "identificador  único", required=True)
    
    _sql_constraints = [
            ('unique_cuit', 'unique(cuit)', 'El cuit/cuil registrado ya existe')
    ]
    