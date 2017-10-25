# -*- coding: utf-8 -*-

from openerp import models, fields, api

class delsol_vehicle_color(models.Model):
    
    _name = "delsol.vehicle_color"
    
    name = fields.Char("Color",required=True,help="Color del vehículo")