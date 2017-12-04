# -*- coding: utf-8 -*-
'''
Created on 22 de jun. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date, datetime
import pytz


class wizard_change_state(models.TransientModel):
    
    _name = "delsol.wizard_change_state"

    
    change_state_date = fields.Datetime("Fecha",readonly=True,default=datetime.now(pytz.utc))
    
    def _vehicle_states(self):
        return self.env['delsol.vehicle'].fields_get()['state']['selection']
    
    actual_state = fields.Selection(string="Estado Actual", related="vehicle_id.state",required=True)
    
    new_state = fields.Selection(_vehicle_states,string="Nuevo Estado",required=True)
    

    reason = fields.Text("Motivo",required=True)
    
    
    def _default_user_id(self):
        
        return self.env.user.id
    
    def _default_vehicle_id(self):
        return self.env['delsol.vehicle'].browse(self._context.get('active_id'))
    
    vehicle_id = fields.Many2one('delsol.vehicle',default=_default_vehicle_id,required=True,readonly=True)

    user_id = fields.Many2one('res.users', string='Usuario', required=True,default=_default_user_id,readonly=True)

    @api.one
    def change_state(self):
        self.vehicle_id.change_state(self)
        return {'type': 'ir.actions.act_window_close'}
    
    
    