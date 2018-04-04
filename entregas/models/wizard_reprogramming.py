# -*- coding: utf-8 -*-
'''
Created on 22 de jun. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date
import datetime

class wizard_reprogramming(models.TransientModel):
    
    _name = "delsol.wizard_reprogramming"
        
    new_date = fields.Datetime("Nueva fecha y hora de cita",required=True)
    
    new_delivery_date = fields.Datetime("Nueva fecha y hora de entrega",required=True)
    
    responsible = fields.Selection([("concesionaria","Concesionaria"),("cliente","Cliente")],required=True,string="Responsable")
    
    reason = fields.Text("Motivo",required=True)
    
    def _default_delivery_id(self):
        return self.env['delsol.delivery'].browse(self._context.get('active_id'))
    
    delivery_id = fields.Many2one('delsol.delivery',default=_default_delivery_id)
    
    @api.one
    def reprogram(self):
        self.delivery_id.reprogram(self)
        return {'type': 'ir.actions.act_window_close'}
    
    @api.onchange('new_delivery_date')
    def onchange_new_delivery_date(self):
        if bool(self.new_delivery_date):
            delivery_client_date = self.env['delsol.config'].search([('code','=','delivery_client_date')]).value
            delivery_client_date_int = eval(delivery_client_date) 
                
            
            client_before_delivery = datetime.datetime.strptime(self.new_delivery_date, '%Y-%m-%d %H:%M:%S')  - datetime.timedelta(minutes=delivery_client_date_int)
            self.new_date = client_before_delivery.strftime('%Y-%m-%d %H:%M:%S')

    
    