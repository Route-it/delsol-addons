# -*- coding: utf-8 -*-

from openerp import models, fields, api
import cStringIO
import xlrd 
import base64
import os
import sys
import re

class financial_state(models.Model):
    _name = 'delsol.financial_state'

    #   Nombre Accesorio
    #   Precio

    def _get_states(self):
        return [('draft','Borrador'),('proccesed','Procesado'),('builded','Generado'),('presented','Presentado')]

    name = fields.Char(compute="compute_name", store=True, readonly=True)
                       
    @api.depends('dealer_code', 'date_month','state')
    @api.multi
    def compute_name(self):
        for i in self:
            i.name = i.dealer_code +" - "+i.date_month[:7].replace("-","/")+" : "+[item for item in i._get_states() if item[0] == i.state][0][1]
    
    
    state = fields.Selection(_get_states, 
                             default="draft", string="Estado", required=True, readonly=True)

    dealer_code = fields.Selection([('061','Autos (061)'),('2071','Camiones (2071)')],string="Código del concesionario")
    
    date_month = fields.Date("Fecha a presentar")
    presented = fields.Date("Fecha descarga o upload a FIS",readonly=True)
    
    rows = fields.One2many(comodel_name="delsol.financial_state_row",inverse_name="financial_state_id",
                           string="Estados financieros",ondelete='cascade',domain=[('register_type','=','dato')])
    
    financial_state_excel = fields.Binary(string="Excel")    
    financial_state_excel_fname = fields.Char(string="File Name")
    
    financial_state_fis = fields.Binary(string='Archivo DAT.')
    financial_state_fis_fname = fields.Char(string="File Name")


    financial_state_excel_visible = fields.Boolean(compute="view_process_excel",store=False)

    def view_process_excel(self):
        self.financial_state_excel_visible = self.financial_state_excel_fname
    
    
    def evaluar_formula(self, r, key_values):
        variables = filter(lambda x:(x != "") & (not x.isdigit()), re.split('[-/+*() ]', r.calculation_formula))
        for i in variables:
            if i not in key_values:
                key_values[i] = self.calcular_valor(r, key_values, i)
                self.create_row(r,key_values[i])
        
        formula_value = eval(r.calculation_formula, key_values)
        return formula_value


    def calcular_valor(self, r, key_values,code):
        try:
            if code != False:
                calculation_formula_for_code = self.env['delsol.financial_state_row'].search([('code','=',code),('calculation_formula','!=',False),('register_type','=','config')])
                if (calculation_formula_for_code == False)|(len(calculation_formula_for_code)==0):
                    try:
                        formula_value = eval(code,key_values)
                    except:
                        #print code + " no esta configurado. Retornando Valor por Defecto"
                        formula_value = self.eval_value(r.default_value)
                else:
                    formula_value = self.evaluar_formula(calculation_formula_for_code, key_values, )
            else:
                formula_value = self.evaluar_formula(r, key_values)
        except Exception as e:
            #si falla porque los valores de la formula no existen en key_values, lo hago recursivo.
            try:
                if "unsupport" not in e.message:
                    formula_value = self.calcular_valor(r,key_values,e.message.split("'")[1].split("'")[0])
                else:
                    formula_value = self.eval_value(r.default_value)
            except Exception as e2:
                formula_value = self.eval_value(r.default_value)
                #print (code or r.code) + "/" + str(r.excel_row) + "/"+ str(r.calculation_formula) + "/"+ str(r.excel_col)
        return formula_value

    
    def create_row(self, r, excel_value):
        
        rows_excel = self.env['delsol.financial_state_row'].search([('code','=',r.code),('financial_state_id','=',self.id),('register_type','=','dato')])

        datas = {
                'name':r.name,
                'description':r.description,
                'code':r.code,
                'phase':1,
                'value_money':excel_value if isinstance(excel_value, (float,int))  else False,
                'value_str':excel_value if isinstance(excel_value, (str,unicode)) else False,
                'register_type':'dato',
                'excel_sheet':r.excel_sheet,
                'excel_col':r.excel_col,
                'excel_row':r.excel_row,
                'default_value':r.default_value,
                'calculation_formula':r.calculation_formula,
                'financial_state_id':self.id,
                }
        if (len(rows_excel)>0)&(r.phase==1):
            rows_excel[0].update(datas)
            return rows_excel[0].id            
        else:
            return self.env['delsol.financial_state_row'].create(datas)
            
    def eval_value(self,default_value):
        if bool(default_value):
            if default_value.replace('.','').isdigit():
                return float(default_value)
            else:
                return default_value
        else:
            return ""
    
    
    @api.multi
    def process_excel(self):
        self.ensure_one()
        recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        
        rows_excel = self.env['delsol.financial_state_row'].search([('excel_col','!=',False),('excel_row','!=',False),('calculation_formula','=',False),('register_type','=','config')])#
        excel_binary = self.financial_state_excel.decode('base64')
        key_values = {}

        for r in rows_excel:
            
            workbook2 = xlrd.open_workbook(file_contents=excel_binary)
            sheet = workbook2.sheet_by_name(r.excel_sheet)
            
            excel_value = sheet.cell_value(r.get_excel_row(), r.get_excel_col())
            self.create_row(r,excel_value)
            
        rows_formula = self.env['delsol.financial_state_row'].search([('excel_col','=',False),('excel_row','=',False),('register_type','=','config'),('phase','=',1)])
        

        for k in self.rows:
            if bool(k.value_money):
                key_values[k.code] = k.value_money
            elif bool(k.value_str):
                key_values[k.code] = self.eval_value(k.value_str)
            elif bool(k.default_value):
                key_values[k.code] = self.eval_value(k.default_value)
            else:
                key_values[k.code] = 0
                                
        for r in rows_formula:
           
                """
                convertir lista en diccionario
                a = ['bi','double','duo','two']
                dict((k,2) for k in a)
                {'double': 2, 'bi': 2, 'two': 2, 'duo': 2}
                """
                
                try:
                    formula_value = self.calcular_valor(r,key_values,False)
                    #formula_value = eval(r.calculation_formula,key_values)
                    self.create_row(r,formula_value)
                    key_values[r.code] = formula_value
                except Exception as e:
                    print "exception on "+r.code+":"+str(formula_value)
                    pass
                
                ##fill only for debug
                #print "as"
                
                """
                reemplazar string (formula) con disccionario (valores)
                dictionary = {"NORTH":"N", "SOUTH":"S" } 
                for key in dictionary.iterkeys():
                address.upper().replace(key, dictionary[key])
                """

        rows_phases = self.env['delsol.financial_state_row'].search([('excel_col','=',False),('excel_row','=',False),('register_type','=','config'),('phase','>',1)])

        for r in rows_phases:
            formula_value = self.evaluar_formula(r, key_values)
            self.create_row(r,formula_value)

                
        sys.setrecursionlimit(recursion_limit)
        self.state = 'proccesed'
                
                #self.fill_dict(key_values,formula_splited)



    @api.multi
    def make_dat(self):

        output = cStringIO.StringIO()

        output.write("{:0<92}".format("H"))
        output.write("\r\n")

        for i in self.rows:
            output.write(
                "{:0>5}".format(self.dealer_code[:5])
            )
            output.write(
                "{:0>2}".format(self.date_month[2:4])
            )
            output.write(
                "{:0>2}".format(self.date_month[5:7])
            )
            output.write(
                "{:<4}".format(i.code[:4])
            )
            
            if bool(i.value_computed):
                try:
                    value = float(i.value_computed)
                except:
                    value = i.value_computed
                if isinstance(value, (float)):
                    output.write(
                        "{:.2f}".format(value)
                    )
                else:
                    output.write(
                        i.value_computed[:120]
                    )
            else:
                output.write(
                        i.default_value
                )
            output.write("\r\n")

        # T0098300000000000000000000000000000000000000000000000000000000000000000000000000000000000000
        output.write("T00")
        output.write("{:0>3}".format(len(self.rows)))
        output.write("{:0<86}".format(""))
        output.write("\r\n")
        
        self.financial_state_fis = base64.encodestring(output.getvalue())
        
        dealer_code = "{:0>5}".format(self.dealer_code[:5])

        self.financial_state_fis_fname = "EFN" + dealer_code + ".DAT"
        
        output.close()
        
        self.state = 'builded'
    
    
    
    
    @api.multi
    def clean_all(self):
        self.rows.unlink()
        self.financial_state_fis = False
        self.financial_state_fis_fname = False
        self.state = 'draft'

    
    @api.multi
    def upload_dat(self):
        
        up_fsf = self.env['delsol.upload_financial_state_fis']
        up_fsf.process(self,'autos')
        
        return
        
        
    """    
    # para procesar el excel con un boton
    @api.multi
    def process_excel(self):
        self.ensure_one()

        escribir en un archivo temporal el excel
        abrir el excel
        obtener todas las filas "financial state row:config" ordenadas por las que tienen fila,columna primero
        para cada fila:
            valor: si hay fila columna, obtenerla del excel
            valor: si hay calculo, buscar en rows y calcular su valor.
            creando un nuevo registro "financial state row:data" con valor
            agregar el valor a rows
            
        eliminar el excel temporal
        
            
    # descargar archivo dat
    @api.multi
    def download_dat(self):
                                        Longitud    desde     hasta
            
        Columna1    concesionario           5    1    5    
        Columna2    Año periodo             2    6    7    
        Columna3    Mes periodo             2    8    9    
        Columna4    D56(IMPORTE LARGO PLAZO)4    10    13    
        Columna5    Valor                   120    14    134    NULL

        
        para cada self.rows:
            dealer_code + date_month:year + date_month:month + row.code + row.valor
        
        write file.
            
        return file.

    

    
    workbook2 = xlrd.open_workbook("C:\Users\Sistemas\Documents\ITSur\Clientes\DelSol\Estados Financieros\Salida\EFAS 061 11-2019.xlsx")
    sheet = workbook2.sheet_by_name("Hoja 1")
    
    #obtiene el valor
    print sheet.cell_value(6, 3)
    #obtiene el objeto Cell
    print sheet.cell(6, 3)
    
    """
