
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class formality(models.Model):
    
    _inherit = 'delsol.formality'

    nro_registro_seccional = fields.Char("Numero de Registro Seccional")
    nro_control_recibo = fields.Char("Numero de Control Recibo")
    nro_control_web = fields.Char("Numero de Control Web")
