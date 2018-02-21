
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
import random


_logger = logging.getLogger(__name__)

class wizard_formality_state(models.Model):
    _name = "dnrpa_formality_state.wizard_formality_state"
    
    captcha_dnrpa = fields.Binary(string='AntiRobot')

    captcha_text = fields.Char("Texto de la imagen")
    
    """
    
    @api.one
    def _compute_dni(self):
        res_partner_id = self.env['res.partner'].browse(self._context.get('active_id'))
        self.dni = self.res_partner_id.vat[2:10]
    """
    @api.one
    def get_formality_state_from_dnrpa(self,args):
        try:
            
            for rec in self:
                
                with open(str(args['active_id'])) as f:
                    s = pickle.load(f)
                    payload = {'captchaCode':str(rec.captcha_text),'_':str(s.cookies._now) }
                    #url = "https://www2.jus.gov.ar/dnrpa-consultatramite/EstadoTramite/IsValidCaptcha?captchaCode="+str(rec.captcha_text)+'&_='+str(s.cookies._now)
                    url = "https://www2.jus.gov.ar/dnrpa-consultatramite/EstadoTramite/IsValidCaptcha?captchaCode="+ urllib.urlencode(payload)
                    #resp = s.get(url=url,data=payload)
                    resp = s.get(url=url)
                    
                    #is_valid_captcha = bool(resp.content) 
                    
                    if (resp.ok & (resp.status_code == 200) & bool(resp.content)):

                        formality_id = self.env['delsol.formality'].browse(args['active_id'])
                        reg_seccional = formality_id.nro_registro_seccional            
                        control_recibo = formality_id.nro_control_recibo            
                        control_web = formality_id.nro_control_web            
                        payload = {'codigoRS':reg_seccional,'numeroControl':control_recibo,'codigoValidacion':control_web }

                        #?codigoRS=9000&numeroControl=9000&codigoValidacion=1234567890&_=1499295005569
                        url = "https://www2.jus.gov.ar/dnrpa-consultatramite/EstadoTramite/ObtenerEstadoDetalle?" + urllib.urlencode(payload)
                        
                        resp = s.get(url)
                        json_resp = json.loads(resp.content) 
                        #do something with json resp
                        
                        #res_partner_id.constancia_cuil_pdf = base64.encodestring(resp.content)
                        #res_partner_id.filename_constancia_cuil = "Constancia - "+ res_partner_id.name+".pdf"
                    else:
                        raise Warning(_('El texto de la imagen es invalido'))
        except Warning:
            raise
        except Exception as e:
            raise Warning("Error: Intente nuevamente o dirijase al sitio de dnrpa\\n"+e.message)
            
        finally:
            self.unlink()
            
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def default_get(self, fields):
        res = super(wizard_formality_state, self).default_get(fields)

        if 'captcha_dnrpa' in fields:
                s = Session()
                r = s.get("https://www2.jus.gov.ar/dnrpa-consultatramite/EstadoTramite/CaptchaImage?"+str(random.random()))
                res.update({'captcha_dnrpa': base64.encodestring(r.content)})

                with open(str(self._context['active_id']), 'w') as f:
                    pickle.dump(s, f)

        return res
