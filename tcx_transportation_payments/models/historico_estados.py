from odoo import fields, models, api


class HistoricoEstados(models.Model):
    _name = "historico.estados"
    _description = "Gestión del historico de estados por documento"

    state = fields.Char("Estado", required=True)
    date = fields.Date("Fecha", required=True)
    action = fields.Char("Accion", required=False)
    user = fields.Char("Responsable", required=True)
    observation = fields.Text(string="Observaciones")
    solicitud_id = fields.Many2one("pago.transporte")
