from odoo import models, fields, api


class DebugTest(models.Model):
    _name = 'debug.test'
    _description = 'Modelo de Testing para Auto-Reload'

    name = fields.Char(string='Nombre', required=True, default='Contador Test')
    count = fields.Integer(string='Contador', default=0, required=True)
    text = fields.Char(string='Texto', default='Texto de prueba 2')
    description = fields.Text(string='Descripción')

    @api.model
    def get_welcome_message(self):
        """Método que retorna un mensaje - perfecto para testing de auto-reload"""
        return "¡Bienvenido al laboratorio de auto-reload! Versión 3.0"

    def nuevo_metodo_test(self):
        return "¡Este es un método nuevo!"