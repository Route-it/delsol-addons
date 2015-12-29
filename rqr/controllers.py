# -*- coding: utf-8 -*-
from openerp import http

# class Rqr(http.Controller):
#     @http.route('/rqr/rqr/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rqr/rqr/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('rqr.listing', {
#             'root': '/rqr/rqr',
#             'objects': http.request.env['rqr.rqr'].search([]),
#         })

#     @http.route('/rqr/rqr/objects/<model("rqr.rqr"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rqr.object', {
#             'object': obj
#         })