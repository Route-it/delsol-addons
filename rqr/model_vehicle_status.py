# -*- coding: utf-8 -*-

from openerp import models, fields, api


class delsol_vehicle_status(models.Model):
    _name = 'delsol.vehicle_status'
    

    STATES = [("new","Nueva"),
                               ("not_chequed","Unidad A Chequear"),
                               ("ready_for_programmed","Lista Para Programar"),
                               ("damage","Unidad Averiada"),
                               ("repaired_damage","Unidad Reparada"),
                               ("missing","Unidad Faltante"),
                               ("to_be_delivery","A Preparar"),
                               ("ready_for_delivery","Lista para entregar"),
                               ("dispatched","Despachado"),
                               ("delivered","Entregado")
                               ]

    PRIORITY = [("normal","Normal"),
                               ("high","Alta")]


    vehicle_id = fields.Many2one("delsol.vehicle",string ="Vehiculo",readonly=True)

    priority_of_chequed_request = fields.Selection(PRIORITY,default="normal",string="Prioridad",required=True,readonly=True)
    
    status = fields.Selection(STATES ,default="new",string="Estado",readonly=True)
    date_status = fields.Datetime("Fecha de cambio de estado",readonly=True)
    comments = fields.Text("Comentarios")
