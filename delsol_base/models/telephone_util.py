# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''
import re

#import logging

#from openerp import models, fields, api, _


#_logger = logging.getLogger(__name__)

#class delsol_delivery(models.Model):
#class delsol_delivery():
    

#    _inherit = ["delsol.delivery"]


def validate_null_tel(mobile):
    if (mobile is None) or (not bool(mobile)) or (len(mobile.strip())<6):
        print "error"
        raise Exception("Telefono incompleto o nulo") 


def clean_tel(mobile):
    mobile = mobile.replace(" ","").replace(".","").replace("-","").replace(")","").replace("(","").replace("#","").replace("|","")
    if "/" in mobile:
        print "posible 2 tels"
        if len(mobile)>10:
            tels = mobile.split("/") # me quedo con el primero. El segundo puede ser asi 154924655/56/57 o 492465/485765 Si es 11/456789 -> invalido
            for te in tels:
                if len(te)>6:
                    mobile = te
                    break;
            if len(tels[0])<5:
                print "ojo, el telefono resultante puede ser invalido."
    
    if mobile.startswith("0"):
        print "el nro inicia con 0, se quita"
        mobile = mobile[1:] # se quita el 0       

    if not mobile.isdigit():
        result = re.search('[a-zA-Z]+',mobile)
        if not (result is None):
            mobile = mobile[:result.regs[0][0]]
            print "no es decimal, quitando parte alpha:" + mobile
        
    return mobile


def normalize_tel_sin_15(mobile):
    if "15" in mobile:
        print "el nro posee 15"
        tef = mobile.split("15",1) # separo telefono de caracteristica, solo una ocurrencia
        if len(tef)>1:    
             caracteristica = tef[0]
             numero = tef[1]
        else:
             numero = tef[0]
             
        if (len(numero)>=6) & (len(caracteristica)>=2) & (len(caracteristica)<=5) & \
            (caracteristica.startswith("1") or caracteristica.startswith("2") or caracteristica.startswith("3")):
            print "numero >= 6 y caracteristica valido"
            numero = caracteristica + numero
        else:
            if mobile.startswith("15"):
                print "numero arranca con 15. Normalizando"
                numero = "297"+numero
            else:
                print "numero invalido, habia 15, pero era algo como 297 461589"
                numero = mobile
    else:
        numero = mobile    
    return numero


def get_delivery_client_mobile(mobile):
        #client = self.client_id
        
        #phone = client.phone
        #mobile = client.mobile
        print "validating:" + mobile

        caracteristica = ""
        numero = ""
        
        validate_null_tel(mobile)        

        mobile = clean_tel(mobile)

        mobile = normalize_tel_sin_15(mobile)
            
        if numero.startswith("1") or numero.startswith("2") or numero.startswith("3"):
            print "posee caracteristica"
        else: 
            print "agregamos la de comodoro por defecto"
            numero = "297" + numero

        print "el numero resultante es:"+ numero
        if len(numero)!= 10:
            return "error"
        return numero


if __name__ == '__main__':


        assert get_delivery_client_mobile("0297 15 4924655")=="2974924655"
        assert get_delivery_client_mobile("0297 4924655")=="2974924655"
        assert get_delivery_client_mobile("297 15 4924655")=="2974924655"
        assert get_delivery_client_mobile("154924655")=="2974924655"
        assert get_delivery_client_mobile("2974924655")=="2974924655"
        assert get_delivery_client_mobile("2971515155")=="2971515155"
        assert get_delivery_client_mobile("492464")=="error"
        assert get_delivery_client_mobile("4924655 int 15/16/17")=="2974924655"
        assert get_delivery_client_mobile("0351 15 4564560") == "3514564560"
        assert get_delivery_client_mobile("011 15 42561244") == "1142561244" 
        assert get_delivery_client_mobile("1142561244") == "1142561244" 
        assert get_delivery_client_mobile("02954 15 428750") == "2954428750"
        assert get_delivery_client_mobile("0111524516564") == "1124516564"
        assert get_delivery_client_mobile("4256125/4267895") == "2974256125"
        assert get_delivery_client_mobile("42561245") == "error"
        assert get_delivery_client_mobile("11 42561545") == "1142561545"
        assert get_delivery_client_mobile("11-42561245 ") == "1142561245"
        assert get_delivery_client_mobile("11/42561245 ") == "error" 
        assert get_delivery_client_mobile("011 42561245") == "1142561245"
        assert get_delivery_client_mobile("4256245") == "2974256245"
        assert get_delivery_client_mobile(" ") == "error"
        assert get_delivery_client_mobile("") == "error"
        
