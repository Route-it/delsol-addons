# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit
from datetime import date, datetime
import pytz

class delsol_vehicle_notify(models.Model):

    _inherit = ["delsol.vehicle"]
        
    @api.one    
    def ready_for_programmed(self):
        super(delsol_vehicle_notify, self).ready_for_programmed()

        users = self.env['res.users'].search([])

        if ((len(users.ids) >0)&(self.priority_of_chequed_request == "high")): 
            for u in users:
                if u.has_group("entregas.group_name_admin_entregas"):
                    msg = '%s Se ha chequeado.' % self.name
                    u.notify_info(msg)

