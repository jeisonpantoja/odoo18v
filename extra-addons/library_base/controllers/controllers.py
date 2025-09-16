# -*- coding: utf-8 -*-
# from odoo import http


# class LibraryBase(http.Controller):
#     @http.route('/library_base/library_base', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/library_base/library_base/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('library_base.listing', {
#             'root': '/library_base/library_base',
#             'objects': http.request.env['library_base.library_base'].search([]),
#         })

#     @http.route('/library_base/library_base/objects/<model("library_base.library_base"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('library_base.object', {
#             'object': obj
#         })

