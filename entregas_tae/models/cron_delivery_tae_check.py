# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import pytz

import datetime
import logging

_logger = logging.getLogger(__name__)


class delsol_delivery_tae_check(models.Model):

    _auto = False

    _name = "delsol.delivery_tae_check"
     
    base_url = "https://www.concesionarios.ford.com"

    def process_key(self, driver, user_fis, password_fis, clave, modo):
    
        # login
        driver.find_element_by_id("FSNloginUserIdInput").send_keys(user_fis) 
        driver.find_element_by_id("FSNloginPasswordInput").send_keys(password_fis)
        driver.find_element_by_xpath("//*[@id='DEALER-WSLXloginBody']/center/form/p/input").click()
        
        
        try:
            if "Login" in driver.find_element_by_xpath("//*[@id='FSNauthAuthFailure1']").text:
                try:
                    delsol_mail_server = self.env['delsol.mail_server']
                    body = "La password del usuario %s en FIS, es incorrecta. Por favor modifiquela en el menu 'Configuracion Del Sol' de ODOO" %  user_fis
                    #delsol_mail_server.send_mail("La password del usuario %s en FIS, es incorrecta. Por favor modifiquela en el menu 'Configuracion Del Sol' de ODOO" %  self.user_fis,body,[("tguerrero@delsolautomotor.com.ar")])
                    delsol_mail_server.send_mail("ODOO - Error de acceso a FIS",body,[("diego@routeit.com.ar")])
                finally:
                    return
        except Exception as e:
            print e
        
        
        """
        # fecha de expiracion de password:  //*[@id='FSNauthSuccess']/td/div[3]/center/table/tbody/tr/td/center
        # Your password will expire on Nov 29, 2018
        
        Se puede obtener la fecha de expiracion y cambiarla con el boton "cambiar password"
          
        """
        #FSNBody > td > table:nth-child(3) > tbody > tr > td:nth-child(1) > center > form > input[type="button"]
        
        
        # continuar
        try:
            driver.find_element_by_xpath("//*[@id='FSNauthSuccess']/td/div[4]/center/table/tbody/tr/td[1]/center/form/input").click()
        except Exception as e:
            driver.find_element_by_xpath("//*[@id='FSNBody']/td/table[2]/tbody/tr/td[1]/center/form/input").click()


        # aceptar alerta
        driver.find_element_by_xpath("/html/body/div[1]/table/tbody/tr[2]/td/form/div/div/table/tbody/tr[4]/td/input").click()
        
        # seleccionar autos o camiones
        if modo == "tradicional":
            if clave == "autos":
                driver.find_element_by_xpath("//*[@id='rowsId']/tbody/tr[1]/td[1]/img").click()  # autos
            else:
                driver.find_element_by_xpath("//*[@id='rowsId']/tbody/tr[2]/td[1]/img").click()  # camiones
    
        # opcion de menu consulta de tae
        driver.get(self.base_url + "/fisdealer/ConsultaTAEActionInit.do")
        
        # click en boton buscar
        driver.find_element_by_xpath("/html/body/div/table/tbody/tr[3]/td/form/div/div/table/tbody/tr[8]/td/input").click()
        
        # revisamos los ultimos 50. Por defecto el listado trae 100
        for x in range(1, 50):
            try:
                nro_chasis = driver.find_element_by_xpath("//*[@id='tae']/tbody/tr[" + str(x) + "]/td[1]").text
                tae_create_date_str = driver.find_element_by_xpath("//*[@id='tae']/tbody/tr[" + str(x) + "]/td[2]").text 
                tae_update_date_str = driver.find_element_by_xpath("//*[@id='tae']/tbody/tr[" + str(x) + "]/td[4]").text 
                tae_status = driver.find_element_by_xpath("//*[@id='tae']/tbody/tr[" + str(x) + "]/td[5]").text 
                
                tae_create_date = datetime.datetime.strptime(tae_create_date_str, '%d/%m/%Y %H:%M:%S') 
                tae_update_date = datetime.datetime.strptime(tae_update_date_str, '%d/%m/%Y %H:%M:%S') 
                
                delivery_s = self.env['delsol.delivery'].search([('vehicle_id.nro_chasis', '=', nro_chasis)])
                if len(delivery_s) == 1:
                    delivery = delivery_s[0]
                    
                    if (delivery.tae_stamp == False):
                        #delivery.message_post(body="El vehiculo está entregado en FIS, pero no en ODOO!")
                        delivery.tae_stamp = tae_create_date
                    # else:
                    #    tae_stamp_date = datetime.datetime.strptime(delivery.tae_stamp, '%Y-%m-%d %H:%M:%S') > tae_create_date 
                    #    if (tae_stamp_date > tae_create_date):
                    #        delivery.tae_stamp = tae_create_date
                    #        delivery.message_post(body="Se ha modificado la fecha de carga de tae")
    
                    if (not bool(delivery.tae_fis_status)):
                        self.update_tae(delivery,tae_update_date,tae_status)
                    if (type(delivery.tae_fis_status) is unicode): 
                        if ("Aceptada" not in delivery.tae_fis_status.encode('ascii', 'ignore')):
                            self.update_tae(delivery,tae_update_date,tae_status)
                    if ((type(delivery.tae_fis_status) is str)):
                        if ("Aceptada" not in str(delivery.tae_fis_status)):
                            self.update_tae(delivery,tae_update_date,tae_status)
                            
            except Exception as e:
                logging.info(e.object + " - " + e.reason)


    def update_tae(self,delivery,tae_update_date,tae_status):
        delivery.tae_update_date = tae_update_date
        delivery.tae_fis_status = tae_status
        delivery.message_post(body="Se ha actualizado el estado de tae")

    def get_driver(self):
        chrome_options = webdriver.ChromeOptions() 
        # para produccion
        # chrome_options.add_argument("headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.implicitly_wait(30)
        return driver

    @api.model
    def process(self,option=None,mode=None):
        logging.info("iniciando cron delivery_tae_check")
        driver = self.get_driver()
        try:
            if (option != None):
                if (option in ("autos","camiones")):
                    if (mode != None):
                        if (mode in ("tradicional","planes")):
                            print "a"
                            driver.get(self.base_url + "/fisdealer/fpw.jsp")
                
                            user_autos_fis = self.env['delsol.config'].search([('code', '=', 'user_'+option+'_'+mode+'_fis')]).value 
                            password_autos_fis = self.env['delsol.config'].search([('code', '=', 'password_'+option+'_'+mode+'_fis')]).value
                            logging.info("cron delivery_tae_check: buscando Taes de "+option)
                            self.process_key(driver, user_autos_fis, password_autos_fis, option,mode)
                    
                            driver.quit()
            # separar las 3 llamadas en 3 crones con parametros diferentes
            """
            driver.get(self.base_url + "/fisdealer/fpw.jsp")

            user_autos_fis = self.env['delsol.config'].search([('code', '=', 'user_autos_fis')]).value 
            password_autos_fis = self.env['delsol.config'].search([('code', '=', 'password_autos_fis')]).value
            logging.info("cron delivery_tae_check: buscando Taes de autos")
            self.process_key(driver, user_autos_fis, password_autos_fis, "autos","tradicional")
    
            driver.quit()
            """                
            """
            driver = self.get_driver()
            driver.get(self.base_url + "/fisdealer/fpw.jsp")

            user_camiones_fis = self.env['delsol.config'].search([('code', '=', 'user_camiones_fis')]).value
            password_camiones_fis = self.env['delsol.config'].search([('code', '=', 'password_camiones_fis')]).value
            logging.info("cron delivery_tae_check: buscando Taes de camiones")
            self.process_key(driver, user_camiones_fis, password_camiones_fis, "camiones","tradicional")

            driver.quit()
            driver = self.get_driver()
            driver.get(self.base_url + "/fisdealer/fpw.jsp")
            
            user_planes_fis = self.env['delsol.config'].search([('code', '=', 'user_planes_fis')]).value
            password_planes_fis = self.env['delsol.config'].search([('code', '=', 'password_planes_fis')]).value
            logging.info("cron delivery_tae_check: buscando Taes de planes")
            self.process_key(driver, user_planes_fis, password_planes_fis, "autos","planes")
            """

        except Exception as e:
            logging.info("Finalizo el cron de actualizacion de taes con errores")
        finally:        
            driver.quit()
            
        logging.info("Finalizo el cron de actualizacion de taes.")

        
