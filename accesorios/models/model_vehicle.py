# -*- coding: utf-8 -*-

from openerp import models, fields, api


class delsol_vehicle(models.Model):
    _name = 'delsol.vehicle'

    _inherit = ["delsol.vehicle"]

    accesories_contact_ids = fields.One2many("delsol.accesories_contact","vehicle_id",string ="Accesorios")

    accesories_contact = fields.Boolean("Contactado",compute="is_accesories_contact",store=True,default=False)

    accesories_installed = fields.Boolean("Contactado",compute="is_accesories_installed",store=True,default=False)

    delivery_date = fields.Datetime(related="delivery_id.delivery_date",readonly=True)
    sector = fields.Selection(related="delivery_id.sector",readonly=True)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if name:
            args += ['|','|',("client_id", operator, name),("nro_chasis", operator, name)] # domain o client_id o name
        return super(delsol_vehicle, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.depends('accesories_contact_ids')
    @api.one
    def is_accesories_contact(self):
        is_contacted = False
        for acc_contact in self.accesories_contact_ids:
            is_contacted = is_contacted | (acc_contact.state == 'contacted')
            if is_contacted: break
            
        self.accesories_contact = is_contacted
        return is_contacted

    @api.depends('accesories_contact_ids')
    @api.one
    def is_accesories_installed(self):
        is_installed = False
        for acc_contact in self.accesories_contact_ids:
            is_installed = is_installed | (acc_contact.state_install == 'colocado')
            if is_installed: break
            
        self.accesories_installed = is_installed
        return is_installed
