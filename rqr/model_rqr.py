# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from time import time
from datetime import datetime
from lxml import etree

class delsol_rqr(models.Model):
    _name = 'delsol.rqr'

    _inherit = ["mail.thread", "ir.needaction_mixin"]
    
    name = fields.Char(compute="name_get", store=True, readonly=True)
    
    delivery_id = fields.Many2one("delsol.delivery", String="Entrega relacionada")
    
    responsible_id = fields.Many2one("hr.employee",String="Responsable")

    tipo_rqr = fields.Many2one("delsol.rqr_type","Tipo de RQR")
    
    sector = fields.Char("Sector")    
    depto = fields.Char("Departamento")   
    
    #state = fields.Many2one('delsol.rqr_state','Etapa',  copy=False)
    state = fields.Selection([('new','Nuevo'),
                                 ('progress','En progreso'),
                                 ('solved','Resuelta'),
                                 ('closed','Cerrado'),
                                 ],string="Estado",required=True,default="new")


    cause = fields.Text(string='Causa')
    delay_resolution = fields.Integer("Demora Resolucion (Dias)",compute="compute_delay",readonly=True,store=True)
    
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
        
        return res



    #Sirve para modificar la vista
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(delsol_rqr, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=False)
        context = self._context or {}
        if bool(view_type) & (view_type == 'form') & bool(context.get('delivery_id')):
            #doc = etree.XML(res['arch'])
            #for node in doc.xpath("//field[@name='delivery_id']"):
                #node.set('domain', "[('id', '=', "+str(context.get('delivery_id'))+")]")#str(context.get('delivery_id')))
            #    node.set('readonly', "True")
            #res['arch'] = etree.tostring(doc)
            for field in res['fields']:
                if field == 'delivery_id':
                    res['fields'][field]['readonly'] = True
            #        res['fields'][field].update({'defaults': context.get('delivery_id')})
        return res

    @api.onchange('state')
    def onchange_state(self):
        self.compute_delay()

    @api.constrains('state')
    def check_have_actions(self):
        if bool(self.state) & (self.state == 'solved'):
            if len(self.corrective_action_ids)<1:
                ValidationError("Para cerrarlo, debe tener al menos una accion correctiva.")
                return
        
    @api.depends('state')
    def compute_delay(self):
        result = 0
        if bool(self.state) & (self.state == 'solved'):
            #print (datetime.now() - self.create_date)
            difference = (datetime.utcnow() - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S'))
            result = difference.days
        else:
            result = 0
        self.delay_resolution = result
        return
    
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
                state =  str(record.state)
                
            
            return delivery +', '+tipo_rqr + ' ('+state+')'
    
    

    def _read_group_state_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        if context is None:
            context = {}
        
        state_obj = self.pool.get('delsol.rqr_state')
        order = state_obj._order
        #access_rights_uid = access_rights_uid or uid
        if read_group_order == 'state_id desc':
            order = '%s desc' % order
        search_domain = []
        state_ids = state_obj._search(cr, None, search_domain, order=order, access_rights_uid=access_rights_uid, context=context)
        result = state_obj.name_get(cr, access_rights_uid, state_ids, context=context)
        # restore order of the search
        result.sort(lambda x, y: cmp(state_ids.index(x[0]), state_ids.index(y[0])))
        fold = {}
        for state in state_obj.browse(cr, access_rights_uid, state_ids, context=context):
            fold[state.id] = state.fold or False
        return result
    
    _group_by_full = {
        #'state': _read_group_state_ids,
        'state': {"new":False,"progress":False,"solved":False},
    }

    
    
    #
    # si state pasa a resuelto, entonces se deben poner todas las acciones correctivas
    # con fecha de fin.
    #
    #
    
    