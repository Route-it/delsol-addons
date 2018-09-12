
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

from PIL import Image
from io import BytesIO
from requests import Session,Request

import logging
import base64
import pickle
import json
import re


_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    """
    captcha_anses = fields.Binary( string='Anses Captcha', store=False)

    captcha_text = fields.Char("Captcha",store=False)
    
    cookie_pickled = fields.Char(store=False)

    @api.multi
    def get_certificate_cuil_from_anses(self):
        url = "http://www.anses.gob.ar/autoconsultas/cuil.php"
        for rec in self:
            payload = {'tipodoc':'0029','numdoc':'35199918','nombre':'Maximiliano','apellidocasada':'',
                       'apellido':'Aciar Ochoa','fechnacimiento':'24/10/1984','sexo':'M','captcha':rec.captcha_text}
    
            with open(str(rec.id)) as f:
                s = pickle.load(f)
            #s = pickle.loads(rec.cookie_pickled)

                resp = s.post(url=url,data=payload)        
        #req = Request('POST',  url, data=payload)
        #prepped = req.prepare()
        #resp = s.send(prepped)
        #resp = s.send(prepped)
        #resp = s.post(url,payload)
        print(resp.text)
    """
    """
    @api.model
    def default_get(self, fields):
        res = super(res_partner, self).default_get(fields)

        #@api.multi
        #def get_captcha_from_anses(self):
        s = Session()
        r = s.get("http://www.anses.gob.ar/autoconsultas/captcha.php?2498187733519")

        i = Image.open(BytesIO(r.content))
        i.save('d:\\out.bmp')

        "ESTO FUNCIONA, pero no puedo reconocer la imagen
        s = Session()
        r = s.get("http://www.anses.gob.ar/autoconsultas/captcha.php?2498187733519")
        ayload = {'tipodoc':'0029','numdoc':'35199918','nombre':'Maximiliano','apellidocasada':'',
                   'apellido':'Aciar Ochoa','fechnacimiento':'24/10/1984','sexo':'M','captcha':''}
        url = "http://www.anses.gob.ar/autoconsultas/cuil.php"
        resp = s.post(url=url,data=payload)
        /autoconsultas/cuilPDF.php?cuil=" + data.datos.cuil + postData       
        myd = json.loads(resp.content[1:]) 
        self.vat = myd['datos']['cuil']
        "

        if 'captcha_anses' in fields:
                res.update({'captcha_anses': base64.encodestring(r.content)})

                with open(str(rec.id), 'w') as f:
                    pickle.dump(s, f)

        #for rec in self:
        
        #    rec.captcha_anses = base64.encodestring(r.content)
        #    with open(str(rec.id), 'w') as f:
        #            pickle.dump(s, f)


        #r.cookies
        #t.text --> <img src=""
        #<RequestsCookieJar[Cookie(version=0, name='PHPSESSID', value='d9599d745a53feda11747792d00df57f', port=None, port_specified=False, domain='ww
        #w.anses.gob.ar', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True,
        #comment=None, comment_url=None, rest={}, rfc2109=False)]>

            #self.write({'captcha_anses':base64.encodestring(r.content),'cookie_pickled': pickle.dumps(r.cookies)})

            #rec.cookie_pickled = pickle.dumps(s)
        #tesseract 'd:\\out.bmp' 'd:\\out'

        #print pytesseract.pytesseract.image_to_string(Image.open(path))

        #url = "http://www.anses.gob.ar/autoconsultas/cuil.php"
        #payload = {'tipodoc':'0029','numdoc':'26442089','nombre':'Monica','apellido':'Castillo','fechnacimiento':'24/10/2984','sexo':'F','captcha':''}
        
        #resp = requests.post(url,payload,cookies=r.cookies)
        #resp.text
        #u'\n{"success":false,"error":"Error en el c\xc3\xb3digo de imagen."}'
    """


    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            self.name = self.name.title()
    
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            res.append((record.id, self.name_get_str(record)))
        return res


    def name_get_str(self,record):
            name = ''
            cuit = ''
            delivery = ''
            
            if record.name:
                name = record.name
    
            if record.vat:
                cuit = record.vat or ''
            #if record.delivery_ids:
            #    delivery = (str(record.delivery.vehicle_id) +'('+ str(record.delivery.delivery_date) +'), rqr:'+ str(record.delivery.rqr_ids.count)) or ''
            if (len(cuit) > 0):
                return name + ' (' + str(cuit) + ')'  

            return name  





    def validate_null_tel(self,mobile):
        if (mobile is None) or (not bool(mobile)) or (len(mobile.strip())<6):
            return False 
        return True
    
    
    def clean_tel(self,mobile):
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
    
    
    def normalize_tel_sin_15(self,mobile):
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
    
    
    def get_client_mobile(self,mobile=None):
            
            if mobile is None:
                if bool(self.mobile):
                    mobile = self.mobile
                else:
                    self.env.user.notify_warning("El nro de movil no esta establecido. Edite el cliente.")
            caracteristica = ""
            numero = ""
            
            self.validate_null_tel(mobile)        
    
            mobile = self.clean_tel(mobile)
    
            mobile = self.normalize_tel_sin_15(mobile)
                
            if mobile.startswith("1") or mobile.startswith("2") or mobile.startswith("3"):
                print "posee caracteristica"
            else: 
                print "agregamos la de comodoro por defecto"
                mobile = "297" + mobile
    
            print "el numero resultante es:"+ mobile
            if len(mobile)!= 10:
                raise ValidationError("El movil no contiene 10 digitos sin contar 0 y 15")
            return mobile


    @api.constrains('phone','mobile')
    def validate_if_can_contact(self):
        
        if not(self.validate_null_tel(self.phone) | self.validate_null_tel(self.mobile)):
            raise ValidationError("Uno de los campos telefono o movil es requerido.")
        if (self.validate_null_tel(self.mobile)):
            self.get_client_mobile(self.mobile)
            
