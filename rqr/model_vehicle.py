# -*- coding: utf-8 -*-

from openerp import models, fields, api


class delsol_vehicle(models.Model):
    _name = 'delsol.vehicle'

    name = fields.Char(compute="name_get", store=True, readonly=True)

    marca = fields.Char(string ="Marca")
    modelo = fields.Many2one("delsol.vehicle_model",string ="Modelo")
    patente = fields.Char(string ="Patente")
    
    anio = fields.Selection([('2015', '2015'),
                                   ('2016','2016'),
                                   ('2017','2017')],
                                  'Modelo Año', required=True, copy=False)
    
    _defaults = {
        'marca': 'Ford'
    }
    
    
    @api.constrains('patente')
    def check_patente(self):
        for record in self:
            pat = record.patente
            if not pat[3:6].isdigit:
                raise ValidationError("El campo patente no posee los 3 numeros.")
                return

            if not pat[0:3].isalpha:
                raise ValidationError("El campo patente no posee las 3 letras.")
                return    
            if (len(pat) != 6):
                raise ValidationError("El campo patente debe tener 6 caracteres.")
                return

    @api.onchange('patente')
    def onchange_patente(self):
        if self.patente:
            self.patente = str(self.patente).upper()

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, self.name_get_str(record)))

        return res

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
        
            return str(marca) + '/' + str(modelo) + ' (' +str(year)+') ' + patente  
