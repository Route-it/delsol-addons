# -*- coding: utf-8 -*-
'''
Created on 21 de jun. de 2016

@author: seba
'''
from openerp import models, fields, api
from openerp.exceptions import ValidationError, Warning
from datetime import date

class delsol_reprogramming(models.Model):
    
    _name = "delsol.reprogramming"
    
    from_date = fields.Datetime("Fecha anterior",readonly=True)
    to_date = fields.Datetime("Nueva fecha",readonly=True)
    
    responsible = fields.Selection([("concesionaria","Concesionaria"),("cliente","Cliente")],string="Responsable",required=True)
    
    reason = fields.Text("Motivo",required=True)
    
    delivery_id = fields.Many2one("delsol.delivery")
    
    
    