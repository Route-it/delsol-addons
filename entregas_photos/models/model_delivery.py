# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba

'''

import logging
import mimetypes

from openerp import models, fields, api, _


_logger = logging.getLogger(__name__)

class delsol_delivery(models.Model):
    
    _inherit = ["delsol.delivery"]

    """
    accesories_contact_ids = fields.One2many("delsol.accesories_contact","vehicle_id",string ="Accesorios")

    delivery_photos_ids = fields.One2Many("")
    accesories_ids = fields.Many2many(comodel_name="delsol.accesories",relation="delsol_accesories_contact_accesories"
                                  ,column1="accesories_contact_id",column2="accesories_id"
                                  ,string="Accesorios solicitados")
    """
    
    delivery_photos_ids = fields.Many2many('ir.attachment', string='Agregar Imagenes')
    delivery_images_sended = fields.Boolean(string="Imagenes ya enviadas?",default=False)



    @api.multi
    def send_delivery_images_to_client(self):
        self.ensure_one()
        if (self.client_email):
            
            result_search = self.env['ir.attachment'].search([('res_id','=',self.id),('res_model','=',self._name),'|',('mimetype','ilike','image'),('mimetype','ilike','video')])
            
            to_delete = result_search - self.delivery_photos_ids
            
            to_delete.unlink()
            
            attachs = []
            for index,photo in enumerate(self.delivery_photos_ids,start=1):
                extension = mimetypes.types_map.keys()[mimetypes.types_map.values().index(photo.mimetype)]
                attachs.append((self.client_id.name+'.'+photo.name+'_'+str(index)+extension,photo.datas.decode('base64')))
            

            mail_obj = self.env['ir.mail_server']
            body = "Hola "+self.client_id.name +"!!\n"
            body += "\t Le adjuntamos las imagenes de la entrega de su vehiculo.\n"
            body += "\t Del Sol Automotor le desea felicidades por su compra.\n"
            
             
            body += "\n\n Este mail es automatico. Por favor no lo responda.\n"
    
            IrMailServer = self.env['ir.mail_server']
            msg = IrMailServer.build_email(
                email_from="sistemas@delsolautomotor.com.ar",
                email_to=[("diego.richi@gmail.com")],
                subject="Felicidades!! le desea Del Sol Automotor",
                body= body,
                attachments = attachs,#[(filename, filecontents)],
                reply_to="sistemas@delsolautomotor.com.ar",
                )
            
            msg_id = IrMailServer.send_email(message=msg,
                              smtp_server="smtp.office365.com",
                              smtp_encryption="starttls",
                              smtp_port="587",
                              smtp_user="sistemas@delsolautomotor.com.ar",
                              smtp_password="Pabo6058"
                              )


            self.delivery_images_sended = True
            self.env.user.notify_info('Las fotos se enviaron con éxito!.')
        else:
            self.env.user.notify_info('El cliente no posee el email cargado.')
