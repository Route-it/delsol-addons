
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class client(models.Model):
    
    _inherit = 'res.partner'

    constancia_cuil_pdf = fields.Binary('Constancia de Cuil',attachment=True, filename="filename_constancia_cuil")
    filename_constancia_cuil = fields.Char("Nombre del Archivo")
