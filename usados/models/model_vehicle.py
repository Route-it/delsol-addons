# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from datetime import date, datetime
import pytz



class delsol_vehicle(models.Model):
    _name = ''

    _inherit = ["delsol.vehicle"]


    is_used = fields.Boolean("Es usado", track_visibility='onchange', default=False)


