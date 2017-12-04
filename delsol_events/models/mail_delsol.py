# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba
'''

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from datetime import date

import logging

_logger = logging.getLogger(__name__)

class delsol_mail_server(models.Model):
    
    _auto = False
    
    _name = "delsol.mail_server"
     
    @api.model
    def send_mail(self,psubject,pbody,pto): 

        smtp_server_name = self.env['delsol.config'].search([('code','=','server_smtp')]).value

        IrMailServer = self.env['ir.mail_server'].search([('name','=',smtp_server_name)])
        
        msg = IrMailServer.build_email(
            email_from=IrMailServer.smtp_user,
            email_to=['diego.richi@gmail.com'],
            #email_to=pto,
            subject=psubject,
            body=pbody,
            subtype="html",
            )

        logging.debug("Cuerpo del mail:"+pbody)

        msg_id = IrMailServer.send_email(message=msg,
                  mail_server_id=IrMailServer.id)
        """
          smtp_server="smtp.office365.com",
          smtp_encryption="starttls",
          smtp_port="587",
          smtp_user="sistemas@delsolautomotor.com.ar",
          smtp_password="Runa9366"
        """
        