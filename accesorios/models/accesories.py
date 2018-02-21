# -*- coding: utf-8 -*-

from openerp import models, fields, api

class accesories(models.Model):
    _name = 'delsol.accesories'

    #   Nombre Accesorio
    #   Precio

    name = fields.Char("Nombre de accesorio")

    price = fields.Monetary("Valor final",currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Moneda",default=lambda self:self.env.user.company_id.currency_id)
    
    vehicle_model_id = fields.Many2one("delsol.vehicle_model","Modelo al que aplica")
