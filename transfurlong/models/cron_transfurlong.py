
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''
import logging
import urllib

from bs4 import BeautifulSoup
from requests import Session, Request

from openerp import models, fields, api


_logger = logging.getLogger(__name__)


class cron_transfurlong(models.Model):
    _name = "delsol.cron_transfurlong_state"

    _auto = False
    
        
    @api.model
    def get_state_from_transfurlong(self):
        try:
            s = Session()
            payload = {'codigo':'00061','marca':'001','password':'automoto','remitir':'Ingresar'}

            url_login= "http://www.transfurlong.com.ar/Prioridades/ValidarUsuario.do"
            r = s.post(url=url_login,data=payload)
            soup = BeautifulSoup(r.content,"lxml")

            url_aprio= "http://www.transfurlong.com.ar/Prioridades/Aprioridades.do"
            payload = {'PDCCNRDE':'61','PDCCCLIE':'1','PDCCPASS':'AUTOMOTO','dia':soup.find('input',{'name':'dia'}).get('value')}
            r = s.post(url=url_aprio,data=payload)

            url_listadoVehiculos= "http://www.transfurlong.com.ar/Prioridades/ListoVehiculos.do"
            
            estados = {
            'C': 'En Playa',
            'F': 'Deposito',
            'I': 'A Enviar',
            'L': 'En Viaje',
            'O': 'Entregada'}
            
            kount = 0
            for i in ('C','F','I','L','O'):
                print estados[i] 
                payload = {'sigla':i}
                r = s.post(url=url_listadoVehiculos,data=payload)
            
                soup = BeautifulSoup(r.content,"lxml")


                table = soup.body.find(id='row')
                
                if not (table is None): 
                    filas = table.find_all('tr')
                    for fila in filas:
                        chasis = fila.td.text[0:17]
                        
                        chasis_corto = chasis[9:]
                        
                        vehicles = self.env['delsol.vehicle'].search([('nro_chasis','ilike',chasis_corto)])
                        
                        if len(vehicles)==1:
                            vehicle = vehicles[0]
                            if (vehicle.transfurlong_state != 'Entregada'):
                                vehicle.transfurlong_state = estados.get(i)
                        else:
                            print 'No se procesa:' + chasis_corto
                        kount += 1

            print 'cantidad'+ str(kount)
        except Exception as e:
            raise Warning("Error: Intente nuevamente mas tarde\\n"+e.message)
        finally:
            print 'Done'

