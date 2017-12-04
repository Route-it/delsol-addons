# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from sre_parse import isdigit


class delsol_vehicle(models.Model):
    _name = 'delsol.vehicle'

    _inherit = ["delsol.vehicle"]

    def _get_states(self):
        list = super(delsol_vehicle, self)._get_states()
        list.append(("formality","En Gestoria"))


    patente = fields.Char(string ="Patente")

    formality_ids = fields.One2many("delsol.formality","vehicle_id",string="Tramites de gestoria") 

    """
    @api.one
    def state_formality(self):
        self.date_for_calendar = False
        self.state = 'formality'
        super(delsol_vehicle, self)._update_status_list()
    """
        
        
    _sql_constraints = [
            ('vehicle_patente_unique', 'unique(patente)', 'La patente ya existe'),
    ]
    
    
    @api.constrains('patente')
    def check_patente(self):
        for record in self:
            pat = record.patente
            if not bool(pat): return
            anio = record.anio
            if ((len(pat) != 6) and (len(pat) != 7)):
                raise ValidationError("El campo patente debe tener 6 o 7 caracteres.")
                return
            elif (len(pat) == 6) & (int(anio) < 2017) :
                if not pat[3:6].isdigit():
                    raise ValidationError("El campo patente no posee los 3 numeros.")
                    return
                if not pat[0:3].isalpha():
                    raise ValidationError("El campo patente no posee las 3 letras.")
                    return    
            elif (len(pat) == 7) & (int(anio) >= 2016):
                if not pat[0:2].isalpha():
                    raise ValidationError("Los primeros dos dígitos de la patente no son letras")
                    return
                if not pat[2:5].isdigit():
                    raise ValidationError("Los d{igitos 3 4 y 5 deben ser números")
                    return
                if not pat[5:7].isalpha():
                    raise ValidationError("Los últimos dos dígitos deben ser números")
                    return
            # Se quita la obligacion de cargar patente.
            # Revisar en que momento hay que obligar cargarla.
            else: 
                raise ValidationError("La patente es invalida")
                return
                
    @api.onchange('patente')
    def onchange_patente(self):
        if self.patente:
            self.patente = str(self.patente).upper()
    
    @api.depends('marca','modelo','patente','anio')
    @api.multi
    def compute_name(self):
        super(delsol_vehicle,self).compute_name()
        for vehi in self:
            vehi.name = vehi.name_get_str(vehi)

    def name_get_str(self, record):
        name_s_pat = super(delsol_vehicle,self).name_get_str(record)
        patente = ''
        if record.patente:
            patente = ('/'+str(record.patente)) or ''
        
        return name_s_pat + patente  
