from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class CartaContratoRel(models.Model):
    _name = "tcx_carta.contrato.rel"
    _description = "Relación de cartas de porte con contratos"

    def _get_domain_contratos(self):
        contratos = (
            self.env["tcx_contratacion.contrato"]
            .sudo()
            .search([("estado_contrato", "=", "Oficializado")])
        )
        arr_ids = []

        for c in contratos:
            arr_ids.append(c.id)
        return [("id", "in", arr_ids)]

    contrato_id = fields.Many2one(
        "tcx_contratacion.contrato",
        string="Contratos",
        domain=_get_domain_contratos,
        required=True,
    )
    carta_id = fields.Many2one("carta.porte", string="Cartas de Porte")

    @api.onchange("carta_id")
    def validar_locaciones(self):

        if self.carta_id:
            raise ValidationError("Prueba")
