# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from datetime import date, datetime
import datetime
from email.message import Message
from exceptions import Exception
import logging

import requests

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning


_logger = logging.getLogger(__name__)

class delsol_import_vehicles(models.Model):
    
    _name = "delsol.invoiced_vehicle_imp"

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

            cuit_l = row.get('CUIT_CUIL').replace('-','')
            c_data = {'vat':cuit_l}
            res_partner = client_obj.search([('vat','=',cuit_l)])
            
            apellido = row.get('Apellido') if (row.get('Apellido') !=False) else ''

            if (row.get('EstadoCivil') == 'Empresa'):
                nombre = row.get('Nombre')
            else:
                nombre = row.get('Nombre_Aux') + ' '+ apellido 

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
                
                
            if ((len(celular)== 0 | len(telefono)==0)& (len(email)==0)):
                print 'El cliente no tiene forma de contactarlo!.'
                #permitir cargar igual el cliente.
                #return

            #verificar 0 (codigo de area 1,2,3) y 15 + nro
            #si es celular -> 
                #ponerlo en celular
                #quitar 0 y 15
            #si es fijo -> 
                # 
                
            #normalizar telefono
            if not (len(celular)==0):
                c_data['mobile'] = celular
            if not (len(telefono)==0):
                c_data['phone'] = telefono
                if (len(celular)==0):
                    c_data['mobile'] = telefono
                
            cod_post = row.get('CodigoPostal')  if not (row.get('CodigoPostal') is None) else ''
            if not (len(cod_post)==0):
                c_data['zip'] = cod_post
            localidad = row.get('Localidad') if not (row.get('Localidad') is None) else ''
            if not (len(localidad)==0):
                c_data['city'] = localidad.lower().title()

            direccion = row.get('Direccion') if not (row.get('Direccion') is None) else ''

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
                if len(res_partner)>0:
                    res_partner[0].write(c_data)
                    client = res_partner[0]    
                else:
                #parner do not exist
                #create partner
                    client = client_obj.create(c_data)    
        except Exception as e:
            print e
            #collect info to send by email
        try:
            ################ END PARNER UPDATE ###############
            ################ BIGIN MODEL UPDATE ###############
            
            model_obj = self.env['delsol.vehicle_model']
            bianchi_modelo = row.get('Modelo')

            model = model_obj.search([('name','ilike',bianchi_modelo.upper()[-4:])])
            
            #TODO: run uppercase to delsol.vehicle_model.name

            if len(model)>0:
                model = model[0]
            else:
                vehicle_type = 'auto'
                model_description = row.get('DescripcionOperativa')
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
            bianchi_u_id = row.get('UnidadID')

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
                      'patente':patente
                      }
            #row.get('PromesaEntregaFecha')
            if len(vehicle)==0:
                print 'crear vehiculo'
                vehicle = vehicle_obj.create(v_data)
                #envio a chequear el vehiculo
                #vehicle.not_chequed()
                #si es camion, no se manda a chequer.
            else:
                if bool(patente):
                    for v in vehicle:
                        v.write({'patente':patente,
                                 'nro_chasis':row.get('Carroceria').upper()})
                vehicle = vehicle[0]
                
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
            #else:
            #    formality = formality[0]
            #    if bool(patente):
            #        formality.write({'patente':patente}) 
            #        if state not in ('completed','finalized'):
            #            formality.write({'state':'completed'}) 

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

            query = 'select * '  
            query += ' from Unidades as u, Colores as c, Preventas as p, Comprobantes as cc, Clientes as cli, Modelos as mo'
            query += '    where  '
            query += '    cc.unidadID = u.UnidadID '
            query += '    and ( cc.CuitCuilDNI = cli.Codigo OR cc.CuitCuilDNI = cli.CUIT_CUIL)'
            query += '    and p.UnidadID = u.UnidadID '
            query += '    and c.ColorID = u.color '
            query += '    and u.Modelo = mo.Modelo '
            query += '    and cc.Fecha > Convert(varchar(30),\''+fecha_hoy+'\',121) '
            query += '    and preventa is not null and Preventa != \'\' '
            query += '    and u.Entregada = 0 '
            query += '    and cc.Anulada = 0 '
            query += '    and u.IDFabrica is not null '
            query += '    and p.TipoDeVentaID in (1,2,3,6,7,8)' #--0km,po,vda,0kmc,vdc,poc '
            query += '    and u.Facturada = 1 '
            query += '    and mo.Origen in (1,2) '# -- autos,camiones
            query += '    and cc.Tipo = \'Automoviles\' and cc.Origen = \'VTOKM\' and cc.Documento = \'FC\' '
    
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
                
