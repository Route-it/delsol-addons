# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class delsol_formality_type(models.Model):
    _name = 'delsol.formality_type'


    number = fields.Char('Numero',required=True)
    description = fields.Char("Descripcion")

