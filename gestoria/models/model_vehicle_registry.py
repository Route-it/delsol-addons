# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from Cython.Plex.Lexicons import State


class delsol_vehicle_registry(models.Model):
    _name = 'delsol.vehicle_registry'


    name = fields.Char('Nombre',required=True)
    address = fields.Char("Direccion")
    tel = fields.Char("Telefono")
    code = fields.Char("Codigo/Numero de Registro",required=True)
    city = fields.Char("Ciudad",required=True)
    res_partner_id = fields.Many2one("res.partner",string="Gestor")

    @api.one
    def name_get(self):
        nom = self.name or ''
        nro = self.nro or ''
        cit = self.city or ''
        return (self.id,str(nom) + ' nro:' + str(nro) + ' - ' + str(cit))
        
        
        