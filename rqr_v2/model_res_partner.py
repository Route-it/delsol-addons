
# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class client(models.Model):
    
    _inherit = 'res.partner'
    
    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(client, self).default_get(fields)

        if ('supplier' in fields) & (bool(context.get("supplier")) == True):
            res.update({'supplier': True})
            res.update({'customer': False})
        if ('customer' in fields) & (bool(context.get("customer")) == True):
            res.update({'supplier': False})
            res.update({'customer': True})
        if ('employee' in fields) & (bool(context.get("employee")) == True):
            res.update({'employee': True})
        
        return res

    
    