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

class delsol_events(models.Model):
    
    _name = "delsol.event"
     
    name = fields.Char("Nombre",readonly=True)
    code = fields.Char("Codigo",readonly=True)
    emails = fields.Char("Mails",help="lista de mails, separados por coma")
    
    active = fields.Boolean("Activo", default=False)

