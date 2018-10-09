# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api,_
from openerp.exceptions import ValidationError, Warning
from email.message import Message
from datetime import date, datetime

import logging
import requests
import datetime

_logger = logging.getLogger(__name__)

class delsol_imported_vehicles(models.Model):
    
    _name = "delsol.vehicle_imp"


    bianchi_vehicle_id = fields.Integer("id de la base de datos")

    vehicle_id = fields.Many2one("delsol.vehicle")
    