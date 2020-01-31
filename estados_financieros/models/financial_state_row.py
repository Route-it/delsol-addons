# -*- coding: utf-8 -*-

from openerp import models, fields, api

class financial_state_row(models.Model):
    _name = 'delsol.financial_state_row'


    name = fields.Char("Nombre del Estado")
    description = fields.Char("Descripcion del campo")
    code = fields.Char("Codigo")

    financial_state_id = fields.Many2one("delsol.financial_state", "Estado financiero")
    
    value_money = fields.Monetary("Valor Monetario",currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Moneda",default=lambda self:self.env.user.company_id.currency_id)
    value_str = fields.Char("Valor String")

    value_computed = fields.Char("Valor",compute="_compute_value")
    

    excel_sheet = fields.Char("Nombre de hoja del excel") 
    excel_col = fields.Char("Columna del excel (ej:AR)") 
    excel_row = fields.Char("Fila del excel (ej:46)")
         
    calculation_formula = fields.Char("Formula de calculo")

    register_type = fields.Selection([("config","Configuracion"),("dato","Dato")],string="Tipo",required="True",default='dato')
    
    @api.one
    def _compute_value(self):
        if bool(self.value_money):
            self.value_computed = str(self.value_money)  
        else:
            self.value_computed = self.value_str 
        
        return self.value_computed
    
    
    def get_excel_row(self):
        return int(self.excel_row)-1
    
    def get_excel_col(self):
        """
        chr(N)->ch;ord(ch)->n
        ord('A')=65
        ord('Z')=90
        """
        if (self.excel_col):
            if (self.excel_col.isnumeric()): return int(self.excel_col) 
            
            n = 25 * (len(self.excel_col)-1) 
            col = ord(self.excel_col[len(self.excel_col)-1].upper()) - 65
        
        return n + col 