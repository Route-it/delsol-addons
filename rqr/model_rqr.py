# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from time import time
from datetime import datetime

class delsol_rqr(models.Model):
    _name = 'delsol.rqr'
    
    name = fields.Char(compute="name_get", store=True, readonly=True)
    
    delivery_id = fields.Many2one("delsol.delivery", String="Entrega relacionada")
    
    tipo_rqr = fields.Many2one("delsol.rqr_type","Tipo de RQR")
    sector = fields.Char("Sector")    
    depto = fields.Char("Departamento")   
    
    state = fields.Many2one('delsol.rqr_state','Etapa', required=True, copy=False)

    cause = fields.Text(string='Causa')
    
    corrective_action_ids = fields.One2many("delsol.correct_action","rqr_id",string="Acciones correctivas",ondelete='cascade')
 
    delay_resolution = fields.Integer("Demora Resolucion (Dias)",compute="compute_delay",readonly=True,store=True)


    @api.onchange('state')
    def onchange_state(self):
        self.compute_delay()

    @api.constrains('state')
    def check_have_actions(self):
        if self.state:
            if self.state.fold:
                if len(self.corrective_action_ids)<1:
                    raise ValidationError("Para cerrarlo, debe tener al menos una accion correctiva.")
                    return
        
    def compute_delay(self):
        result = 0
        if self.state:
            if self.state.fold:
                #print (datetime.now() - self.create_date)
                result = (datetime.utcnow() - datetime.strptime(self.create_date, '%Y-%m-%d %H:%M:%S')).days
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
            if record.delivery_id:
                delivery =  str(record.delivery_id.name_get_str(record.delivery_id))
            
            return delivery +', '+str(record.tipo_rqr) + ' ('+str(record.state)+')'
    
    

    def _read_group_state_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        if context is None:
            context = {}
        state_obj = self.pool.get('delsol.rqr_state')
        order = state_obj._order
#        access_rights_uid = access_rights_uid or uid
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
        return result, fold
    
    _group_by_full = {
        'state': _read_group_state_ids,
    }

    
    
    #
    # si state pasa a resuelto, entonces se deben poner todas las acciones correctivas
    # con fecha de fin.
    #
    #
    
    