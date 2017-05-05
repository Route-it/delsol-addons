# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from time import time
from datetime import datetime
from lxml import etree

class delsol_rqr(models.Model):
    _name = 'delsol.rqr'

    _inherit = ["mail.thread", "ir.needaction_mixin"]
    
    STATES = [('new','Nuevo'),
                                 ('progress','En progreso'),
                                 ('solved','Resuelta'),
                                 ('closed','Cerrado'),
                                 ]
    
    FOLDED_STATES = [] #['new',]
    

    
    name = fields.Char(compute="name_get", store=True, readonly=True)
    
    delivery_id = fields.Many2one("delsol.delivery", String="Entrega relacionada")
    
    responsible_id = fields.Many2one("hr.employee",String="Responsable")

    tipo_rqr = fields.Many2one("delsol.rqr_type","Tipo de RQR")
    
    sector = fields.Selection([("ovalo","Plan Óvalo"),("especial","Venta Especial"),("tradicional","Venta Tradicional")],string="Sector",required="True")

    #sector = fields.Many2one("hr.department",string="Sector")    
#    depto = fields.Selection([("repuestos","Repuestos"),("admin_plan_ovalo","Administración de Plan Ovalo"),("admin_tradicional","Administración de Venta Tradicional")],string="Departamento")   
    
    state = fields.Selection(STATES,string="Estado",required=True,default="new")
    
    progress_date = fields.Datetime("Fecha en progreso")
    solved_date = fields.Datetime("Fecha de resolucion")
    closed_date = fields.Datetime("Fecha de cierre")


    progress = fields.Float(compute='_get_progress', string='Progreso')


    cause = fields.Text(string='Causa')
    delay_resolution = fields.Integer("Demora Resolucion (Dias)",compute="compute_delay",readonly=True,store=True)

    delay_to_take_action = fields.Integer("Demora en tomar acción (Dias)",compute="compute_delay",default=-1,readonly=True,store=True)
    
    resolution_id = fields.Many2one("delsol.rqr_resolution",string="Resolucion implementada",ondelete='cascade')

    task_ids = fields.Many2many(comodel_name="project.task", relation="project_task_rqr", column1="task_id", column2="rqr_id", string="Acciones Correctivas") 

    call_root_id = fields.Many2one("delsol.call",string="Llamado que la genero",readonly=True)    

    call_ids = fields.One2many(related='delivery_id.call_ids')

    severity = fields.Selection([('0','Baja'),
                                 ('1','Media baja'),
                                 ('2','Media'),
                                 ('3','Media Grave'),
                                 ('4','Grave'),
                                 ('5','Critica')
                                 ],string="Severidad",default="2")

    #Sirve para modificar los valores por defecto de la vista
    @api.model
    def default_get(self, fields):
        context = self._context or {}
        
        res = super(delsol_rqr, self).default_get(fields)

        if ('delivery_id' in fields) & bool(context.get('delivery_id')):
            res.update({'delivery_id': context.get('delivery_id')})
            res.update({'sector': context.get('sector')})
        return res



    #Sirve para modificar la vista
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(delsol_rqr, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        context = self._context or {}

        if bool(view_type) & (view_type == 'form') & bool(context.get('delivery_id')):

            for field in res['fields']:
                if field == 'delivery_id':
                    res['fields'][field]['readonly'] = True
            #        res['fields'][field].update({'defaults': context.get('delivery_id')})
        return res

    @api.onchange('state')
    @api.one
    def onchange_state(self):
        self.compute_delay()
        #if (self.old_state != self.state):
        #    self.write({'old_state': self.state})
        #    self.write({'old_state_date' : datetime.utcnow()})

    @api.one
    def _get_progress(self):
        return 100

    
        
    @api.depends('state')
    @api.one
    def compute_delay(self):
        #result_delay_to_take_action = 0
        #demora en resolver el caso, desde que se dio de alta
        difference_to_take_action = False
        if bool(self.state) & (self.state == 'progress'):
            if self.progress_date == False:
                self.progress_date = datetime.utcnow()
            difference = (datetime.strptime(self.progress_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
            self.delay_to_take_action = difference.days

            
        if bool(self.state) & (self.state == 'solved'):
            #print (datetime.now() - self.create_date)
            #difference = (datetime.utcnow() - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
            
            #calculo dias de demora en reslucion
            if self.solved_date == False:
                self.solved_date = datetime.utcnow()
            difference_delay = (datetime.strptime(self.solved_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
            self.delay_resolution = difference_delay.days
            if self.progress_date == False:
                self.progress_date = self.solved_date
                difference_to_take_action = (datetime.strptime(self.solved_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
            else:
                difference_to_take_action = (datetime.strptime(self.solved_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.progress_date, '%Y-%m-%d %H:%M:%S'))
            self.delay_to_take_action = difference_to_take_action.days
        
        if bool(self.state) & (self.state == 'closed'):
            if self.closed_date == False:
                self.closed_date = datetime.utcnow()
            if self.progress_date == False:
                self.progress_date = self.closed_date
            if self.solved_date == False:
                self.solved_date = self.closed_date
                if bool(self.progress_date == self.solved_date):

                    difference_to_take_action = (datetime.strptime(self.closed_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
                else:
                    difference_to_take_action = (datetime.strptime(self.closed_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.progress_date, '%Y-%m-%d %H:%M:%S'))
            else:
                difference_to_take_action = (datetime.strptime(self.closed_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.solved_date, '%Y-%m-%d %H:%M:%S'))
            self.delay_to_take_action = difference_to_take_action.days

            difference_delay = (datetime.strptime(self.solved_date, '%Y-%m-%d %H:%M:%S') - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
            self.delay_resolution = difference_delay.days

        #demora en cambiar estado, desde el utlimo cambio
        if (bool(self.state) & (self.state == 'new')):
            difference = (datetime.utcnow() - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
            self.delay_to_take_action = difference.days
            
            
    
    @api.depends('delivery_id','tipo_rqr','state')
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            record.name = self.name_get_str(record)
            res.append((record.id, self.name_get_str(record)))
        return res

    
    def name_get_str(self, record):
            delivery = ''
            tipo_rqr = ''
            state = ''
            if record.delivery_id:
                delivery =  str(record.delivery_id.name_get_str(record.delivery_id))
            
            if record.tipo_rqr:
                tipo_rqr =  str(record.tipo_rqr.name_get_str(record.tipo_rqr))
            if record.state:
                #state =  str(record.state.name_get_str(record.state))
                tempstate = record.state or ''
                state =  str(tempstate.encode('utf8'))
                
            
            return delivery +', '+tipo_rqr + ' ('+state+')'
    
    
    @api.model
    def state_groups(self, present_ids, domain, **kwargs):
        folded = {key: (key in self.FOLDED_STATES) for key, _ in self.STATES}
        # Need to copy self.STATES list before returning it,
        # because odoo modifies the list it gets,
        # emptying it in the process. Bad odoo!
        return self.STATES[:], folded

    _group_by_full = {
        #'state': _read_group_state_ids,
        'state': state_groups
                
    }


    def _read_group_fill_results(self, cr, uid, domain, groupby,
                                 remaining_groupbys, aggregated_fields,
                                 count_field, read_group_result,
                                 read_group_order=None, context=None):
        """
        The method seems to support grouping using m2o fields only,
        while we want to group by a simple status field.
        Hence the code below - it replaces simple status values
        with (value, name) tuples.
        """
        if groupby == 'state':
            STATES_DICT = dict(self.STATES)
            for result in read_group_result:
                state = result['state']
                result['state'] = (state, STATES_DICT.get(state))

        return super(delsol_rqr, self)._read_group_fill_results(
            cr, uid, domain, groupby, remaining_groupbys, aggregated_fields,
            count_field, read_group_result, read_group_order, context
        )
    
    
    #
    # si state pasa a resuelto, entonces se deben poner todas las acciones correctivas
    # con fecha de fin.
    #
    #
    
    