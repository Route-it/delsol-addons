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
    _name = "delsol.why_no_contacted"
    
    name = fields.Text(string="Motivo",required=True)
    
