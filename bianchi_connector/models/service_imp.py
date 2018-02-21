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

class delsol_import_services(models.Model):
    
    _name = "delsol.service_imp"


    @api.multi
    def test_sql_server(self):
        try:
            conn = self.env['connector.sqlserver'].search([('name','=','Bianchi')])[0]
            conexion = conn.connect()
            cursor = conexion.cursor() #conn.getNewCursor(conexion)
    
            cursor.execute('select * from Unidades where ' +
                        'preventa is not null and Preventa != \'\' ' +
                        'and Entregada = 0 '+
                        'and IDFabrica is not null '+
                        'order by UnidadID desc '
                        )  
            cursor_list = cursor.fetchall()
            
            
            
            
            for row in cursor_list:
                print "row %s" % (row,)
                
            
            """
            ClienteId,Nombre,Apellido,Nombre_Aux,Codigo,CUIT_CUIL,DNI,
            Direccion,Provincia,Localidad,CodigoPostal, 
            Email, Celular, Telefono, telefonoLaboral
            """ 

            cursor.execute('select * from Clientes '+
                           'where (CUIT_CUIL is not null and CUIT_CUIL != \'\') and '+
                           '( (Email is not null and email != \'\' and email != \'[No Posee]\') or Telefono is not null or TelefonoLaboral is not null '+
                           'or (Celular != \'\' and Celular is not null)) '+
                           'and Activo = 1 ')
            cursor_list = cursor.fetchall()
            
            
            for row in cursor_list:
                print "row %s" % (row,)
                
            
            #row = cursor.fetchone()

            #while row:
            #    print "chasis=%s, motor=%s" % (row['Carroceria'], row['Motor'])
            #    row = cursor.fetchone()
        except e:
            print e
        finally:
            conexion.close()
                
