
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

import base64
from datetime import date, datetime
from io import BytesIO
import json
import logging
import pickle
import urllib

from PIL import Image
from requests import Session, Request

from openerp import _
from openerp import models, fields, api
from openerp.exceptions import ValidationError
from openerp.exceptions import Warning
import time


_logger = logging.getLogger(__name__)

class wizard_constancia(models.Model):
    _name = "anses_cuil.wizard_constancia"

    
    captcha_anses = fields.Binary(string='AntiRobot')

    captcha_text = fields.Char("Texto de la imagen")
    nombre = fields.Char("Nombres")
    apellido = fields.Char("Apellidos")

    dni = fields.Char("DNI")

    """
    
    @api.one
    def _compute_dni(self):
        res_partner_id = self.env['res.partner'].browse(self._context.get('active_id'))
        self.dni = self.res_partner_id.vat[2:10]
    """
    @api.one
    def get_certificate_cuil_from_anses(self,args):
        try:
            url = "http://www.anses.gob.ar/autoconsultas/cuil.php"
            for rec in self:
                
                res_partner_id = self.env['res.partner'].browse(args['active_id'])
                dni = res_partner_id.vat[2:10]            
                nombre = rec.nombre 
                apellido = rec.apellido
                dni = rec.dni 
                payload = {'tipodoc':'0029','numdoc':str(dni),'nombre':str(nombre),'apellidocasada':'',
                           'apellido':str(apellido),'fechnacimiento':'24/10/1984','sexo':'M','captcha':str(rec.captcha_text)}
                
                with open(str(args['active_id'])) as f:
                    s = pickle.load(f)
    
                    resp = s.post(url=url,data=payload)
                    
                    json_resp = json.loads(resp.content[1:]) 
                    
                    if (json_resp['success']):
    
                        url = "http://www.anses.gob.ar/autoconsultas/cuilPDF.php?cuil=" + json_resp.get('datos')['cuil'] +'&'+ urllib.urlencode(payload)
                        
                        resp = s.get(url)
                        res_partner_id.constancia_cuil_pdf = base64.encodestring(resp.content)
                        res_partner_id.filename_constancia_cuil = "Constancia - "+ res_partner_id.name+".pdf"
                    else:
                        raise Warning(_(json_resp['error']))
        except Warning:
            raise
        except Exception as e:
            raise Warning("Error: Intente nuevamente o dirijase al sitio de anses\\n"+e.message)
            
        finally:
            self.unlink()
            
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        res = super(wizard_constancia, self).default_get(fields)


        if 'captcha_anses' in fields:
                s = Session()
                r = s.get("https://www.anses.gob.ar/constancia-de-cuil/")
                r = s.get("http://www.anses.gob.ar/autoconsultas/captcha.php?" + str(int(round((time.time() * 1000) ))))

                res.update({'captcha_anses': base64.encodestring(r.content)})

                with open(str(self._context['active_id']), 'w') as f:
                    pickle.dump(s, f)


        return res
