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
     
    client_id = fields.Many2one('res.partner',string="Cliente",domain = [('customer','=','True')], help = "Cliente asociado al vehiculo",required=True,ondelete='cascade',write=['rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])

    vehicle_id = fields.Many2one('delsol.vehicle',string="Vehiculo", help = "Vehiculo",required=True,write=['rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])

    delivery_date = fields.Datetime(string="Fecha de entrega",required=True,write=['rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])
    
    delay = fields.Integer(default=1)
    
    color = fields.Integer(default=100)

    vendor_id = fields.Many2one("hr.employee",String="Vendedor",write=['rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])
    
    applay_rqr = fields.Boolean("Aplica RQR",write=['rqr.group_name_rqr_delivery_resp','rqr.group_name_rqr_administrator'])
    
    call_ids = fields.One2many('delsol.call','delivery_id',string="Contactos al cliente", help = "Contactos con el cliente",groups="rqr.group_name_rqr_delivery_resp,rqr.group_name_rqr_contact_resp,rqr.group_name_rqr_administrator")
    
    rqr_ids = fields.One2many('delsol.rqr','delivery_id',string="RQRs", help = "RQR asociados a esta entrega",groups="rqr.group_name_rqr_contact_resp,rqr.group_name_rqr_administrator")

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
 
 
    state = fields.Selection([('new','Nueva'),
                              ('reprogrammed','Reprogramada'),
                              ('dispatched','Despachado'),
                              ('delivered','Entregado')],string="Estado",default="new",track_visibility='onchange')
    olddate = fields.Datetime()
    tae_stamp = fields.Datetime("Fecha y hora de carga de TAE",help="Fecha y hora de carga de TAE para saber cuándo aproximadamente llega la encuesta")


    def set_new(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'new'
        
    def set_delivered(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'delivered'
    
    @api.one
    def set_dispatched(self):
        self.state = "dispatched"

    def set_close(self, cr, uid, ids, context=None):
        for record in self.browse(cr, uid, ids, context=context):
            record.state = 'closed'

    @api.onchange('contacted')
    def verify_state(self):
        if self.contacted & (self.state == 'new' | self.state == 'delivered' ):
            self.state = 'contacted'
   
    @api.constrains('delivery_date')
    def set_reprogrammed(self):
        if (self.delivery_date != self.olddate) and (self.olddate is not False):
            self.state = 'reprogrammed'
        self.olddate = self.delivery_date

    @api.one
    def stamp_tae(self):
        if not self.tae_stamp:
            self.tae_stamp = fields.Datetime.now()
        

#    def chek_vehicle_not_delivered(self, cr, uid, ids, context=None):
#        result_search = self.pool.get('delsol.delivery').search(cr, uid, [('vehicle_id','=',self.vehicle_id)], context=context)
#        if len(result_search)>0:
#            result_search

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
        
    def make_poll_rqr(self,cr, uid, ids, context=None):
        rqr_obj = self.pool['delsol.rqr']
        #rqr_state_obj = self.pool['delsol.rqr_state']
        #rqr_state = rqr_state_obj.search(cr, uid, [('sequence','=', 0)])
        
        
        for delivery in self.browse(cr, uid, ids, context=context):
        #check if delivery is delivered.
            if delivery.state != 'delivered':
                raise Warning('La entrega debe estar en estado "Entregado".')
                return
            
            message = 'Ya se posee una rqr generada.'
            
            if not bool(delivery.poll_rqr_id):
                defaults = {'delivery_id': delivery.id,'state':'new'}
                
                target_rqr =  rqr_obj.create(cr, uid, defaults, None)
                
                delivery.poll_rqr_id = target_rqr
                message = 'Se genero correctamente la RQR.'


            """
            warning = {
                        'title': 'Mensaje !',
                        'message': message
                     }
            """
            
            res = {'value': {}}
            warning = {'warning': {
                    'title': 'Mensaje',
                    'message': message,
                    }}        
            res.update(warning)
    
            #return {'warning': warning}
            #return res
            return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                    }