# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class delsol_delivery(models.Model):
    
    _name = "delsol.delivery"

    name = fields.Char(compute="name_get", store=True, readonly=True)
     
    client_id = fields.Many2one('res.partner',string="Cliente",domain = [('customer','=','True')], help = "Cliente asociado al vehiculo",required=True,ondelete='cascade')

    vehicle_id = fields.Many2one('delsol.vehicle',string="Vehiculo", help = "Vehiculo",required=True)

    delivery_date = fields.Datetime(string="Fecha de entrega",required=True)
    
    delay = fields.Integer(default=1)
    
    color = fields.Integer(default=100)

    vendor_id = fields.Many2one("res.partner",String="Vendedor",domain=[("customer",'=',False),("supplier",'=',True)])

    call_ids = fields.One2many('delsol.call','delivery_id',string="Contactos al cliente", help = "Contactos con el cliente")
    rqr_ids = fields.One2many('delsol.rqr','delivery_id',string="RQRs", help = "RQR asociados a esta entrega")

    contacted = fields.Boolean(string="Contactado",compute="is_contacted",store=True)

    answered_poll = fields.Boolean("Contesto encuesta?")
    sales_asistance = fields.Integer("Asesor de ventas",default=3,help="Califique del 1 al 5")
    payment_experience = fields.Integer("Experiencia de pago",default=3,help="Califique del 1 al 5")
    compliance = fields.Integer("Nivel de Cumplimiento",default=3,help="Califique del 1 al 5")
    delivery_process = fields.Integer("Proceso de entrega",default=3,help="Califique del 1 al 5")
    comment_poll = fields.Text("Comentaro")
 
 
    state = fields.Selection([('new','Nueva'),
                              ('delivered','Entregado'),
                              ('contacted','Contactado'),
                              ('closed','Cerrado')],string="Estado",default="new")


    def set_new(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'new'
        
    def set_delivered(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'delivered'

    def set_close(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'closed'

    @api.onchange('contacted')
    def verify_state(self):
        if self.contacted & (self.state == 'new' | self.state == 'delivered' ):
            self.state = 'contacted'


    def chek_vehicle_not_delivered(self, cr, uid, ids, context=None):
        result_search = self.pool.get('delsol.delivery').search(cr, uid, [('vehicle_id','=',self.vehicle_id)], context=context)
        if len(result_search)>0:
            result_search
    
    @api.constrains('vehicle_id')
    def chek_vehicle_not_delivered(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            if bool(record.vehicle_id):
                result_search = self.pool.get('delsol.delivery').search(cr, uid, [('vehicle_id','=',record.vehicle_id.id)], context=context)
                if len(result_search)>1:
                    raise ValidationError("El vehiculo ya fue entregado")
                    return


    @api.depends('call_ids')
    def is_contacted(self,cr, uid, ids, context=None):
        is_contacted = False
        for record in self.browse(cr, uid, ids, context=context):
            for call in record.call_ids:
                is_contacted = is_contacted | call.contacted
                if is_contacted: break
            
            record.contacted = is_contacted
        return is_contacted

    @api.depends('client_id','delivery_date','vehicle_id')
    def name_get(self,cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            record.name = self.name_get_str(record)
            res.append((record.id, self.name_get_str(record)))
        return res
    
    def name_get_str(self,record):
            cliente = ''
            vehiculo = ''
            fecha = ''
                
            if record.client_id:
                cliente = str(record.client_id.name_get_str(record.client_id)) or ''
            
            if record.delivery_date:
                fecha = str(record.delivery_date[0:10])
            
            if record.vehicle_id:
                vehiculo = str(record.vehicle_id.name_get_str(record.vehicle_id)) or ''

            return str(cliente) + '(' + str(vehiculo) + '), ' + fecha  
        
