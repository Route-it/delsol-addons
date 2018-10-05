# -*- coding: utf-8 -*-
'''
Created on 4 de ene. de 2016

@author: seba

Instalacion: 
    instalar selenium
    sudo pip install selenium
    Instalar chrome 
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb 
    sudo dpkg -i google-chrome*.deb 
    sudo apt-get install -f 
    sudo dpkg -i google-chrome*.deb 

    Instalar driver de chrome
    wget https://chromedriver.storage.googleapis.com/2.42/chromedriver_linux64.zip
    unzip chromedriver_linux64.zip
    cp chromedriver /usr/bin/


'''

import logging
from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)

class delsol_delivery(models.Model):
    
    _inherit = ["delsol.delivery"]

    tae_stamp = fields.Datetime(readonly=True)
    tae_update_date = fields.Datetime("Actualizacion de TAE (FIS)",readonly=True)
    tae_fis_status = fields.Char("Estado de TAE (FIS)",readonly=True)

