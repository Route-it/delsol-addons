# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from datetime import date, datetime
import pytz



class delsol_vehicle(models.Model):

    _inherit = ["delsol.vehicle"]
    

    button_create_delivery_visible = fields.Boolean(compute="_button_create_delivery_visible")    


    delivery_id = fields.Many2one('delsol.delivery',string="Entrega", help="Si el vehiculo esta programado, se mostrara aqui", 
                                  readonly=True,compute='_compute_delivery') 


    @api.one
    def _compute_delivery(self):
        result = self.env['delsol.delivery'].search([('vehicle_id','=',self.id)])
        if len(result)==1:
            self.delivery_id = result[0]

    @api.multi
    def _button_create_delivery_visible(self):
            self.ensure_one()
            if bool(self.id):
                result_search = self.env['delsol.delivery'].search([('vehicle_id','=',self.id)])
                if len(result_search)>0:
                    self.button_create_delivery_visible = False
                else:
                    if (self.state not in ('ready_for_delivery','to_be_delivery')):
                        self.button_create_delivery_visible = False
                    else:
                        self.button_create_delivery_visible = True