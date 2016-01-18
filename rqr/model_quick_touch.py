# -*- coding: utf-8 -*-

from openerp import models, fields, api

class delsol_quick_touch(models.Model):
    _name = 'delsol.quick_touch'
    
    name = fields.Char(compute="name_get", store=True, readonly=True)
        
    delivery = fields.Many2one("delsol.delivery",String="Entrega relacionada")

    grado_satisfaccion = fields.Selection([('ms','Muy Satisfecho'),('s','Satisfecho'),('ps','Poco Satisfecho'),('is','Insatisfecho'),('mi','Muy Insatisfecho')],required=True,String="Grado de satisfaccion")
    
    recomienda = fields.Boolean(String="Nos recomienda")
    
    comentario_sugerencia = fields.Text(String="Comentario/Sugerencia")


    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self:
            recomienda = ''
            
            if record.delivery:
                delivery =  str(record.delivery.name_get_str(record.delivery))

            if record.recomienda:
                recomienda = 'Recomienda'
            else: 
                recomienda = 'No Recomienda' 
        
            #if record.delivery_ids:
            #    delivery = (str(record.delivery.vehicle_id) +'('+ str(record.delivery.delivery_date) +'), rqr:'+ str(record.delivery.rqr_ids.count)) or ''
            result = str(recomienda) + '('+delivery+')' 
            res.append((record.id, result))
            
        return res
        