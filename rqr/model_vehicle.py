# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit


class delsol_vehicle(models.Model):
    _name = 'delsol.vehicle'

    name = fields.Char(compute="compute_name", store=True, readonly=True)

    marca = fields.Char(string ="Marca")
    modelo = fields.Many2one("delsol.vehicle_model",string ="Modelo")
    color = fields.Many2one("delsol.vehicle_color",string ="Color de vehículo")
    patente = fields.Char(string ="Patente")
    nro_chasis = fields.Char(string="Nro de Chasis")

    
    anio = fields.Selection([('2014','2014'),
                             ('2015', '2015'),
                             ('2016','2016'),
                             ('2017','2017')],
                             'Modelo Año', required=True, copy=False)
    
    _sql_constraints = [
            ('vehicle_patente_unique', 'unique(patente)', 'La patente ya existe'),
    ]
    
    _defaults = {
        'marca': 'Ford'
    }
    
    
    @api.constrains('patente')
    def check_patente(self):
        for record in self:
            pat = record.patente
            if ((len(pat) != 6) and (len(pat) != 7)):
                raise ValidationError("El campo patente debe tener 6 o 7 caracteres.")
                return
            elif (len(pat) == 6):
                if not pat[3:6].isdigit():
                    raise ValidationError("El campo patente no posee los 3 numeros.")
                    return
                if not pat[0:3].isalpha():
                    raise ValidationError("El campo patente no posee las 3 letras.")
                    return    
            elif (len(pat) == 7):
                if not pat[0:2].isalpha():
                    raise ValidationError("Los primeros dos dígitos de la patente no son letras")
                    return
                if not pat[2:5].isdigit():
                    raise ValidationError("Los dígitos 3 4 y 5 deben ser números")
                    return
                if not pat[5:7].isalpha():
                    raise ValidationError("Los últimos dos dígitos deben ser números")
                    return
                
    @api.onchange('patente')
    def onchange_patente(self):
        if self.patente:
            self.patente = str(self.patente).upper()
    
    @api.depends('marca','modelo','patente','anio')
    @api.multi
    def compute_name(self):
        for vehi in self:
            vehi.name = vehi.name_get_str(vehi)

    def name_get_str(self, record):
            marca = ''
            modelo = ''
            patente = ''
            year = ''
            
            if record.anio:
                #year = self.anio[0:4] usado en caso de campo tipo date.
                year = record.anio
    
            if record.marca:
                marca = record.marca or ''
            if record.modelo:
                modelo = record.modelo.name_get_str(record.modelo) or ''
            if record.patente:
                patente = record.patente or ''
        
            return str(marca.encode('utf8')) + '/' + str(modelo.encode('utf8')) + ' (' +str(year)+') ' + patente  
