# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import datetime
import logging

_logger = logging.getLogger(__name__)

class delsol_process_events(models.Model):
    
    _auto = False
    _name = "delsol.process_rqr_delays"
     
    @api.model
    def process(self):

        logging.info("iniciando cron on_rqr_delays")
        events = self.env['delsol.event'].search([('active','=',True),('code','=','on_rqr_delays')])
        logging.debug("events:"+str(events.ids))
        
        if (len(events.ids) >0 ):
            
            #('active','=',True),
            rqrs = self.env['delsol.rqr'].search([
                                               ('state','in',['new','progress','solved'])
                                               ])
            
            if (len(rqrs.ids) >0 ):
    
                logging.debug("rqrs:"+str(rqrs.ids))
        
                for r in rqrs:
                    r.compute_delay()
                    
            else:
                logging.info("Cron on_rqr_delays: nada para procesar.")
            logging.info("Cron on_rqr_delays completado.")
        else:
            logging.info("Cron on_rqr_delays: nada para procesar.")
        