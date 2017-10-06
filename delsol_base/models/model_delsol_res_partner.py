
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


    @api.constrains('phone','mobile')
    def validate_if_can_contact(self):
        if not(bool(self.phone) | bool(self.mobile)):
            raise ValidationError("Uno de los campos telefono o movil es requerido.")
            return

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

