# -*- coding: utf-8 -*-

from openerp import models, fields, api


class delsol_vehicle(models.Model):
    _name = 'delsol.delivery'

    _inherit = ["delsol.delivery"]


    accesories_contact = fields.Boolean("Contactado por accesorios",related="vehicle_id.accesories_contact",readonly=True)
    
    accesories_installed = fields.Boolean("Accesorios instalados",related="vehicle_id.accesories_installed",readonly=True)


