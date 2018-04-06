# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''
import datetime
import logging
import re

import pytz

from openerp import models, fields, api, _


_logger = logging.getLogger(__name__)

class delsol_delivery(models.Model):
    

    _inherit = ["delsol.delivery"]



    def get_delivery_datetime(self,fecha):
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        fecha_hora = pytz.utc.localize(datetime.datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')).astimezone(local).strftime('%d/%m a la hora %H:%M')
        return fecha_hora


    def send_sms(self,message=None):
        delsol_sms_server = self.env['delsol.sms_server'].search([('name','=','ventas')])[0]
        smsnro = self.client_id.get_client_mobile()


        if not (message is None):
            if not (("batea" in self.client_id.name.lower()) or ("del sol" in self.client_id.name.lower())):
                message = message + " Del Sol Automotor"
                delsol_sms_server.send_sms(message,smsnro)



            


    @api.one
    def stamp_client_arrival(self):
        super(delsol_delivery, self).stamp_client_arrival()

        try:
            #######################################################
            # AVISO AL RESPONSABLE DE ENTREGAS
            #######################################################
            
            modelo = (self.vehicle_id.modelo.description[:15] + '..') if len(self.vehicle_id.modelo.description) > 15 else self.vehicle_id.modelo.description
            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            hora = pytz.utc.localize(datetime.datetime.strptime(self.delivery_date, '%Y-%m-%d %H:%M:%S')).astimezone(local).strftime('%H:%M')
            if bool(self.vehicle_id.patente):
                message = "El cliente "+self.client_id.name +" ha arribado. Hora entrega: "+ hora +". "+modelo +" " + self.vehicle_color +" " + self.vehicle_id.patente
            else:
                message = "El cliente "+self.client_id.name +" ha arribado. Hora entrega: "+ hora +". "+modelo +" " + self.vehicle_color
                mensaje_sin_patente = 'Llego el cliente, el vehiculo no tiene la patente cargada.'
                super(delsol_delivery,self).message_post(body=mensaje_sin_patente)
                self.env.user.notify_info(mensaje_sin_patente)

            delsol_sms_server = self.env['delsol.sms_server'].search([('name','=','odoo')])[0]
            
            if self.vehicle_id.modelo.vehicle_type == 'auto':
                      
                smsnro_sergio = "2974139563" #  Sergio Bellido
                delsol_sms_server.send_sms(message,smsnro_sergio)

            if self.vehicle_id.modelo.vehicle_type == 'camion':
                smsnro_roberto = "2974924655" #  Roberto Arguello
                #delsol_sms_server.send_sms(message,smsnro_roberto)
            
            mensaje_notif_resp_entre = 'Se ha notificado por sms al responsable de entregas.'
            super(delsol_delivery,self).message_post(body=mensaje_notif_resp_entre)
            self.env.user.notify_info(mensaje_notif_resp_entre)



            #######################################################
            # BIENVENIDA AL CLIENTE
            #######################################################

            if self.vehicle_id.modelo.vehicle_type == 'auto':
            
                smsnro_cliente = self.client_id.get_client_mobile()
    
                message_cliente = "Del sol le da la bienvenida y le desea muchas felicidades. La clave de la wifi DEL SOL CLIENTES es delsol2045"
                
                delsol_sms_server.send_sms(message_cliente,smsnro_cliente)
    
                mensaje_cliente_bienvenida = 'Se ha enviado un sms al cliente dandole la bienvenida y la clave de wifi.'
                super(delsol_delivery,self).message_post(body=mensaje_cliente_bienvenida)
                self.env.user.notify_info(mensaje_cliente_bienvenida)

            
        except Exception as e:
            print "Unexpected error!"

    @api.model
    def create(self, vals):
        id = super(delsol_delivery, self).create(vals)
        try:
            user_tz = self.env.user.tz or pytz.utc
            local = pytz.timezone(user_tz)
            fecha_hora = self.get_delivery_datetime(vals['client_date'])

            nombre = ""
            sector = vals['sector']
            if sector == 'ovalo':
                nombre = "Pablo Moncalieri."
            else:
                nombre = "Stefania Lencioni."


            vehicle = self.env['delsol.vehicle'].search([('id','=',vals['vehicle_id'])])[0]
            cliente = vehicle.client_id
            
            message = "Estimado/a "+cliente.name+", Lo esperamos en H. Yrigoyen 2045 el " + fecha_hora + " para la entrega de su " + id.vehicle_id.marca +". "
            message += nombre
            
            if vehicle.modelo.vehicle_type == 'auto':
                id.send_sms(message)
                mensaje_cliente_entrega = 'Se ha notificado al cliente por sms la entrega de la unidad'
                super(delsol_delivery,self).message_post(body=mensaje_cliente_entrega)
                self.env.user.notify_info(mensaje_cliente_entrega)
            
        except Exception as e:
            
            self.env.user.notify_info(e.message)

            _logger.error("No se pudo enviar el sms de aviso de entrega")
            _logger.error(e.message)
        return id

    def reprogram(self,reprogram):
        super(delsol_delivery, self).reprogram(reprogram)
        try:

            if self.vehicle_id.modelo.vehicle_type == 'auto':
                fecha_hora = self.get_delivery_datetime(self.client_date)
                message = "Se ha reprogramado la entrega de su " + self.vehicle_id.marca + " para la fecha " + fecha_hora +". "

                self.send_sms(message)
                
                mensaje_cliente_reprog = 'Se ha notificado al cliente por sms la reprogramacion de la unidad'
                super(delsol_delivery,self).message_post(body=mensaje_cliente_reprog)
                self.env.user.notify_info(mensaje_cliente_reprog)

        except Exception as e:
            
            self.env.user.notify_info(e)

            _logger.error("No se pudo enviar el sms de aviso")
            _logger.error(e.message)


