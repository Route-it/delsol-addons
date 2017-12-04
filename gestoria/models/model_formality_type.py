# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError


class delsol_formality_type(models.Model):
    _name = 'delsol.formality_type'

    name = fields.Char('Nombre')

    number = fields.Char('Numero',required=True)
    description = fields.Char("Descripcion") 

    @api.one
    def name_get(self):
        nom = ''
        if self.description:
            nom = self.description[:15] or ''
        num = self.number or ''
        return (self.id, num + ', ' +nom)
