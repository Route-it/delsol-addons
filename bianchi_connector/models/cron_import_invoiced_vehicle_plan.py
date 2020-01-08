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
from exceptions import Exception

_logger = logging.getLogger(__name__)

class delsol_import_vehicles(models.Model):
    
    _name = "delsol.invoiced_planahorro"

    _auto = False

    """tablas a trabajar
    Colores delsol.vehicle_colorE
    Modelos delsol.vehicle_model
    Vehiculos delsol.vehicle
    Gestoria delsol.formality
    """
    
    vehicle_id = fields.Integer("id de la base de datos")

    row = fields.Char("Fila importada")

    create_date = fields.Datetime("Fecha ejecucion")

    operation = fields.Selection([('c','Creado'),
                                  ('u','Actualizado'),
                                  ('d','Borrado')], string="Operacion")



    def v_import(self,row):
            ################ BIGIN PARNER UPDATE ############### 
        try:

            client_obj = self.env['res.partner']
            state_obj = self.env['res.country.state']
            country_obj = self.env['res.country']
            cuit_l = row.get('CUIT').replace('-','')
            c_data = {'vat':cuit_l}    
            res_partner = client_obj.search([('vat','=',cuit_l)])
            
            apellido = row.get('paapellido') if (row.get('paapellido') !=False) else ''

            if (row.get('paestadocivil') == 'Empresa'):
                    nombre = row.get('razonsocial')
            else:
                    nombre = row.get('panombre') + ' '+ apellido 
                
            nombre = nombre.lower().title()
            c_data['name'] = nombre

            #search provincia in res.country.state. And select or create
            country = country_obj.search([('name','=','Argentina')])[0]
            c_data['country_id'] = country.id

            
            provincia = state_obj.search([('name','=',row.get('Provincia').lower().title())]) 
            
            if len(provincia)>0:
                provincia = provincia[0] 
            else:
                provincia = state_obj.create({'name':row.get('Provincia').lower().title(),
                                              'country_id':country.id,
                                              'code':row.get('Provincia').replace(' ','').upper()[:3]})
            
            c_data['state_id'] = provincia.id


            email = row.get('Email').lower() if not (row.get('Email') is None) else ''
            if not (('no posee' in email) | (len(email)==0) ):
                c_data['email'] = email

            celular = row.get('Celular') if not (row.get('Celular') is None) else ''
            telefono = row.get('Telefono') if not (row.get('Telefono') is None) else ''

            if ((len(celular)== 0 | len(telefono)==0)& (len(email)==0)):
                print 'El cliente no tiene forma de contactarlo!.'
                #permitir cargar igual el cliente.
                #return

            try:
                celular = client_obj.get_client_mobile(celular)
            except Exception as e:
                celular = ''
                print e
            try:
                telefono = client_obj.get_client_mobile(telefono)
            except Exception as e:
                telefono = ''
                print e
                
                
                            
            if not (len(celular)==0):
                c_data['mobile'] = celular
            if not (len(telefono)==0):
                c_data['phone'] = telefono
                if (len(celular)==0):
                    c_data['mobile'] = telefono
                
            cod_post = row.get('codigopostal') if not (row.get('codigopostal') is None) else row.get('CodPost')
            if not (len(cod_post)==0):
                c_data['zip'] = cod_post
            localidad = row.get('Localidad') if not (row.get('Localidad') is None) else ''
            if not (len(localidad)==0):
                c_data['city'] = localidad.lower().title()

            #verificar 0 (codigo de area 1,2,3) y 15 + nro
            #si es celular -> 
                #ponerlo en celular
                #quitar 0 y 15
            #si es fijo -> 
                # 

            
            
            direccion = row.get('Domicilio') if not (row.get('Domicilio') is None) else row.get('Direccion')
            
            direccion = direccion if not (direccion is None) else ''
            
            if not (len(direccion)==0):
                c_data['street'] = direccion.lower().title()
            else:
                "advise that client have empty direction"

                
            c_data['customer'] = True
            #c_data['customer'] = True if (row.get('EstadoCivil') == 'Empresa') else False
            c_data['company_type'] = 'company' if (row.get('EstadoCivil') == 'Empresa') else 'person'
            c_data['notify_email'] = 'none'
            

            #search res.partner and update or create
            if len(res_partner)>0:
                #i found one partner
                #select it
                res_partner[0].write(c_data)
                client = res_partner[0]
            else:
                #no lo encontramos por CUIT/CUIL, lo buscamos por nombre y apellido
                res_partner = client_obj.search(['&',('name','ilike',row.get('Nombre').lower().title()),('name','ilike',apellido.replace(' ','').lower().title())])
                if len(res_partner)==0:
                #parner do not exist
                #create partner
                    client = client_obj.create(c_data)    
                else:
                    res_partner[0].write(c_data)
                    client = res_partner[0]
        except Exception as e:
            print e
            #collect info to send by email
        try:
            ################ END PARNER UPDATE ###############
            ################ BIGIN MODEL UPDATE ###############
            
            model_obj = self.env['delsol.vehicle_model']
            bianchi_modelo = row.get('Modelo')

            model = model_obj.search([('name','ilike',bianchi_modelo.upper()[-4:])])
            

            model_description = row.get('DescripcionOperativa')
            if len(model)>0:
                model = model[0]
            else:
                vehicle_type = 'auto'
                if 'cargo' in model_description.lower(): vehicle_type = 'camion'
                else: 
                    if '4000' in model_description.lower(): vehicle_type = 'camion'
                    else: 
                        if '100' in model_description.lower(): vehicle_type = 'camion'
                        else: 
                            if 'transit' in model_description.lower(): vehicle_type = 'camion'

                m_data = {'name':bianchi_modelo.upper()[-4:],
                      'description':model_description,
                      'turn_duration':60,
                      'vehicle_type':vehicle_type,
                      }
                model = model_obj.create(m_data)    
            if not(model.description) or len(model.description)==0:
                model.write({'description':model_description})
                #ojo con los camiones. No se cumple la regla de 4.
            #Si no viene el modelo, return no se importa el vehiculo.

                
            ################ END MODEL UPDATE ###############
            ################ BEGIN COLOR UPDATE ###############
            
            color_obj = self.env['delsol.vehicle_color']
            bianchi_color = row.get('Descripcion').lower().title() #descripcion del color
            
            color = color_obj.search([('name','=',bianchi_color)]) 
            
            if len(color)>0:
                color = color[0]
            else:
                color = color_obj.create({'name':bianchi_color}) 
            

        except Exception as e:
            print e
            #collect info to send by email

            
            ################ END COLOR UPDATE ###############
            ################ BEGIN VEHICLE UPDATE ###############
            #Al finalizar, enviar un mail con observaciones de la importacion,
            #indicando al menos el cliente-vehiculo

        try:
            vehicle_imp_obj = self.env['delsol.vehicle_imp']
            vehicle_obj = self.env['delsol.vehicle']
            bianchi_u_id = row.get('paunidadid')

            vehicle_imp = vehicle_imp_obj.search([('bianchi_vehicle_id','=',bianchi_u_id)])
            vehicle = vehicle_obj.search([('nro_chasis','ilike',row.get('Carroceria').upper()[-8:])])


            arrival_to_dealer_date = row.get('FechaDeRecepcion') if row.get('Recibida') == True else False
            
            patente = row.get('Patente') if len(row.get('Patente'))>0 else False
            
            anio_produccion = str(row.get('AnioProduccion')) if len(str(row.get('AnioProduccion')))>0 else False
            
            anio_produccion = anio_produccion[0:4]            
            
            v_data = {'client_id':client.id,
                      'modelo':model.id, #id del model
                      'color':color.id,
                      'state':'new',
                      'anio':anio_produccion,
                      'nro_chasis':row.get('Carroceria').upper(),
                      'fecha_facturacion':row.get('FechaContable'),
                      'arrival_to_dealer_date':arrival_to_dealer_date,
                      'patente':patente,
                      'delivery_date_promess':row.get('PromesaEntregaFecha')}
            
            if len(vehicle)==0:
                print 'crear vehiculo'
                vehicle = vehicle_obj.create(v_data)
                #envio a chequear el vehiculo
                #vehicle.not_chequed()
                #si es camion, no se manda a chequer.
            else:
                vehicle = vehicle[0]
                if bool(patente):
                        vehicle.write({'patente':patente})
                vehicle.write({'client_id':client.id,
                                  'modelo':model.id, #id del model
                                  'color':color.id,
                                  'anio':anio_produccion,
                                  'nro_chasis':row.get('Carroceria').upper(),
                                  'fecha_facturacion':row.get('FechaContable'),
                                  'arrival_to_dealer_date':arrival_to_dealer_date,
                                  'delivery_date_promess':row.get('PromesaEntregaFecha')})
                
            if len(vehicle_imp)==0:
                print 'crear vehiculo_imp'
                vehicle_imp = vehicle_imp_obj.create({'bianchi_vehicle_id':bianchi_u_id,'vehicle_id':vehicle.id})
            else:
                vehicle_imp[0].vehicle_id = vehicle.id
            
            # para historial status_obj = self.env['delsol.vehicle_status']

        except Exception as e:
            print e
            #collect info to send by email
        
            
            ################ END VEHICLE UPDATE ###############
            ################ BEGIN GESTORIA UPDATE ###############            
        
        """
        try:
            
            #creo el registro en gestoria, si no existe
            formality_obj = self.env['delsol.formality']
            formality = formality_obj.search([('vehicle_id','=',vehicle.id)])
            if len(formality)==0:
                state = 'new' if (patente == False) else 'completed' 
                formality = formality_obj.create({'vehicle_id':vehicle.id,
                                                  #'formality_type':'01',
                                                  'state':state})
                # relevar en gestoria, los registros
                # relevar los tramites que se realizan: si esta patentado, si no esta patentado.
                
            #collect error and send email advice.
        except Exception as e:
            print e
            #collect info to send by email
        """    
        self.env.cr.commit()


    #@api.multi #call from button
    @api.model #call from cron
    def import_vehicle(self):
        try:
            conn = self.env['connector.sqlserver'].search([('name','=','Bianchi')])[0]
            conexion = conn.connect()
            cursor = conexion.cursor() #conn.getNewCursor(conexion)
    
            hoy_00 = datetime.datetime.today()
            hace_X_dias_00 = hoy_00 - datetime.timedelta(days=15)

    
            fecha_hoy = str(hace_X_dias_00.year) + '-' + str(hace_X_dias_00.month) + '-' + str(hace_X_dias_00.day) 

            query = 'select pa.Nombre as panombre, pa.Apellido as paapellido,'
            query += ' pa.EstadoCivil as paestadocivil, Comprobantes.Nombre as razonsocial, '
            query += ' pa.UnidadID as paunidadid, Comprobantes.CUITCUILDNI as cmpcuitcuil, '
            query += ' pa.CodPost as codigopostal, * '
            #query += ' PlanAhorroSolicitudes.CodPost as codigopostal, Comprobantes.CUITCUILDNI as cmpcuitcuil, * '
            query += ' from (PlanAhorroSolicitudes as pa LEFT JOIN Unidades ON pa.UnidadID = Unidades.UnidadID)'
            query += ' LEFT JOIN Modelos ON Unidades.Modelo = Modelos.Modelo '
            query += ' inner join Comprobantes on pa.ControlGR = Comprobantes.Referencia '
            query += ' inner join Colores on colores.ColorID = unidades.color '
            query += ' WHERE comprobantes.Origen LIKE \'VTGTS%\' And  '
            query += ' Referencia like \'%GR%\' And  '
            query += '  (Comprobantes.Anulada = 0) And  '
            query += '  Comprobantes.Fecha > Convert(varchar(30),\''+fecha_hoy+'\',121) '
            #query += '  Comprobantes.Fecha > ' + fecha_hoy + ' '
            query += '  ORDER BY 1 '

            cursor.execute(query)  
            cursor_list = cursor.fetchall()
            
            vehicle_imp_obj = self.env['delsol.vehicle_imp']
            for row in cursor_list:
                print "importando fila %s" % (row,)
                try:
                    self.v_import(row)
                except Exception as e:
                    print e
                
            
            """
            ClienteId,Nombre,Apellido,Codigo,CUIT_CUIL,DNI,
            Direccion,Provincia,Localidad,CodigoPostal, 
            Email, Celular, Telefono, telefonoLaboral

            cursor.execute('select * from Clientes '+
                           'where (CUIT_CUIL is not null and CUIT_CUIL != \'\') and '+
                           '( (Email is not null and email != \'\' and email != \'[No Posee]\') or Telefono is not null or TelefonoLaboral is not null '+
                           'or (Celular != \'\' and Celular is not null)) '+
                           'and Activo = 1 ')
            cursor_list = cursor.fetchall()
            
            
            for row in cursor_list:
                print "row %s" % (row,)
                
            """ 
            
            #row = cursor.fetchone()

            #while row:
            #    print "chasis=%s, motor=%s" % (row['Carroceria'], row['Motor'])
            #    row = cursor.fetchone()
        except Exception as e:
            self.env.cr.rollback()
            raise e
        finally:
             if conexion != False : conexion.close()
                
