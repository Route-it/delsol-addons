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
import base64
import tempfile
from selenium.webdriver.common import keys
import os

_logger = logging.getLogger(__name__)


class delsol_upload_financial_state_fis(models.Model):

    _auto = False

    _name = "delsol.upload_financial_state_fis"
     
    base_url = "https://www.concesionarios.ford.com"

    def process_key(self, driver, user_fis, password_fis, clave, f_state):
        
        
        driver.find_element_by_xpath("//*[@id='bySelection']/div[2]").click()
    
        # login
        driver.find_element_by_id("DEALER-WSLXloginUserIdInput").send_keys(user_fis) 
        driver.find_element_by_id("DEALER-WSLXloginPasswordInput").send_keys(password_fis)
        driver.find_element_by_xpath("//*[@id='DEALER-WSLXloginWSLSubmitButton']/input").click()
        
        try:
            if "Fallido" in driver.find_element_by_xpath("//*[@id='DEALER-WSLXauthInvalidUser1']").text:
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
        
        
        # continuar by timeout
        #try:
            #driver.find_element_by_xpath("//*[@id='FSNauthSuccess']/td/div[4]/center/table/tbody/tr/td[1]/center/form/input").click()
        #except Exception as e:
            #driver.find_element_by_xpath("//*[@id='FSNBody']/td/table[2]/tbody/tr/td[1]/center/form/input").click()


        # aceptar alerta
        driver.find_element_by_xpath("/html/body/div[1]/table/tbody/tr[2]/td/form/div/div/table/tbody/tr[4]/td/input").click()
        
        # seleccionar autos o camiones
        if clave == "autos":
            driver.find_element_by_xpath("//*[@id='rowsId']/tbody/tr[1]/td[1]/img").click()  # autos
        else:
            driver.find_element_by_xpath("//*[@id='rowsId']/tbody/tr[2]/td[1]/img").click()  # camiones
    
        
        # opcion de menu consulta de tae
        driver.get(self.base_url + "/fisdealer/EnvioArchivosActionPage.do")
        
        # click en boton buscar
        
        #driver.find_element_by_name("filterArchivo").selectByIndex(0)
                
        driver.find_element_by_xpath("/html/body/div/table/tbody/tr[3]/td/form/div/div/table/tbody/tr[2]/td[1]/select/option[2]").click()



        #write temp file
        #fp = tempfile.TemporaryFile('w', suffix='.dat')
        fd, tempfilename = tempfile.mkstemp(suffix='.dat')
        f = os.fdopen(fd,"w")

        fp_content = base64.decodestring(f_state.financial_state_fis)
        f.write(fp_content)
        f.close()

        #driver.find_element_by_xpath('/html/body/div/table/tbody/tr[3]/td/form/div/div/table/tbody/tr[2]/td[2]/input').send_keys("C:/Users/Sistemas/Downloads/EFN00061.DAT")
        driver.find_element_by_xpath('/html/body/div/table/tbody/tr[3]/td/form/div/div/table/tbody/tr[2]/td[2]/input').send_keys(tempfilename)

        #submit!
        driver.find_element_by_xpath("/html/body/div/table/tbody/tr[3]/td/form/div/div/table/tbody/tr[11]/td[1]/input").click()
        
        
        #delete temp file
        os.unlink(tempfilename)
        
        try:
            if "Errores" in driver.find_element_by_xpath("/html/body/div/table/tbody/tr[3]/td/table/tbody/tr[1]/td[1]").text:
                
                #img errores file path
                #driver.find_element_by_xpath("/html/body/div/table/tbody/tr[4]/td/form/form/table/tbody/tr/td/table/tbody/tr[1]/td[6]/img").click()
                
                # nueva pestana
                #driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't')
                
                #https://www.concesionarios.ford.com/fisdealer/VisualizarArchivoAction.do
                #form_data rowSelected: 1 

                #mostrar error en pantalla.
                print "errores"
                return
                #try:
                #    delsol_mail_server = self.env['delsol.mail_server']
                #    body = "Hubo error de validacion del archivo DAT en FIS. Por favor verifique el proceso"
                #    delsol_mail_server.send_mail("ODOO - Error de validacion de DAT de FIS",body,[("diego@routeit.com.ar")])
                #finally:
                #    return
        except Exception as e:
            print e
        
        
        f_state.state = 'presented'
                
        #except Exception as e:
        #        logging.info(e.object + " - " + e.reason)


    def get_driver(self):
        chrome_options = webdriver.ChromeOptions() 
        # para produccion
        # chrome_options.add_argument("headless")
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.implicitly_wait(30)
        return driver

    @api.model
    def process(self,f_state,option=None):
        logging.info("iniciando delsol_upload_financial_state_fis")
        driver = self.get_driver()
        try:
            if (option != None):
                if (option in ("autos","camiones")):
                        driver.get(self.base_url + "/fisdealer/fpw.jsp")
            
                        user_autos_fis = self.env['delsol.config'].search([('code', '=', 'user_financial_state_fis')]).value 
                        password_autos_fis = self.env['delsol.config'].search([('code', '=', 'password_financial_state_fis')]).value
                        self.process_key(driver, user_autos_fis, password_autos_fis, option, f_state)
                        driver.quit()
                        logging.info("Finalizo delsol_upload_financial_state_fis, sin errores")

        except Exception as e:
            logging.info("Finalizo delsol_upload_financial_state_fis, con errores")
        finally:        
            driver.quit()
            
        logging.info("Finalizo la subida del archivo de estados financieros.")

        
