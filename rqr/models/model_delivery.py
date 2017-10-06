# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api,_
from openerp.exceptions import ValidationError, Warning
from email.message import Message
from datetime import date, datetime

import logging
import requests
import datetime

_logger = logging.getLogger(__name__)

class delsol_delivery(models.Model):
    
    _inherit = ["delsol.delivery"]

    applay_rqr = fields.Boolean("Aplica RQR",)
    
    call_ids = fields.One2many('delsol.call','delivery_id',string="Contactos al cliente", help = "Contactos con el cliente")
    
    rqr_ids = fields.One2many('delsol.rqr','delivery_id',string="RQRs", help = "RQR asociados a esta entrega")

    contacted = fields.Boolean(string="Contactado",compute="is_contacted",store=True)
    
    answered_poll = fields.Boolean("Contesto encuesta?")
    sales_asistance = fields.Integer("Asesor de ventas",default=3,help="Califique del 1 al 5")
    payment_experience = fields.Integer("Experiencia de pago",default=3,help="Califique del 1 al 5")
    compliance = fields.Integer("Nivel de Cumplimiento",default=3,help="Califique del 1 al 5")
    delivery_process = fields.Integer("Proceso de entrega",default=3,help="Califique del 1 al 5")
    love_dealer = fields.Integer("Adorar al concesionario",default=3,help="Califique del 1 al 5")
    defense_dealer = fields.Integer("Defensa",default=3,help="Califique del 1 al 5")
    comment_poll = fields.Text("Comentaro")
    poll_rqr_id = fields.Many2one("delsol.rqr", string="RQR", readonly=True)
    

    @api.onchange('contacted')
    def verify_state(self):
        if self.contacted & (self.state == 'new' | self.state == 'delivered' ):
            self.state = 'contacted'
   

    @api.depends('call_ids')
    def is_contacted(self,cr, uid, ids, context=None):
        is_contacted = False
        for record in self.browse(cr, uid, ids, context=context):
            for call in record.call_ids:
                is_contacted = is_contacted | call.contacted
                if is_contacted: break
            
            record.contacted = is_contacted
        return is_contacted

    
        
    def make_poll_rqr(self,cr, uid, ids, context=None):
        rqr_obj = self.pool['delsol.rqr']
        
        
        for delivery in self.browse(cr, uid, ids, context=context):
        #check if delivery is delivered.
            if delivery.state != 'delivered':
                raise Warning('La entrega debe estar en estado "Entregado".')
                return
            
            message = 'Ya se posee una rqr generada.'
            
            if not bool(delivery.poll_rqr_id):
                defaults = {'delivery_id': delivery.id,'state':'new','sector':delivery.sector}
                
                target_rqr =  rqr_obj.create(cr, uid, defaults, None)
                
                delivery.poll_rqr_id = target_rqr
                message = 'Se genero correctamente la RQR.'

            self.browse(cr,uid,ids,context).env.user.notify_info(message)
    
            return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                    }
        