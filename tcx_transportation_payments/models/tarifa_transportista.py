from odoo import api, fields, models
from odoo.addons.modify_model_from_excel_file.models.modify_model_from_excel_file import (
    FROM_EXCEL_FILE_MIXIN_MODEL_NAME,
)
from odoo.addons.tecnotex_servicio_pago_transporte.models.transportista import (
    TRANSPORTISTA_MODEL_NAME,
)

from odoo.tools.translate import _

TARIFA_TRANSPORTISTA_MODEL_NAME = "tarifa.transportista"
CARTA_PORTE_MODEL_NAME = "carta.porte"


class TarifaTransportista(models.Model):
    _name = TARIFA_TRANSPORTISTA_MODEL_NAME
    _description = "Tarifa de Transportistas"

    tarifa_id = fields.Many2one(CARTA_PORTE_MODEL_NAME)

    transportista = fields.Many2one(TRANSPORTISTA_MODEL_NAME, ondelete="cascade")
    origen = fields.Char()
    destino = fields.Char()
    distancia = fields.Integer()
    tipo_contenedor = fields.Char()
    precio_km_ton = fields.Monetary()
    currency_id = fields.Many2one("res.currency", string="Moneda")


class ExcelTransportista(models.Model):
    _inherit = [FROM_EXCEL_FILE_MIXIN_MODEL_NAME, TRANSPORTISTA_MODEL_NAME]
    _name = TRANSPORTISTA_MODEL_NAME

    import_template_id = fields.Many2one(
        readonly=True,
        default=lambda self: self.env.ref(
            "tecnotex_servicio_pago_transporte.tarifa_transportista_excel"
        ).id,
    )
    _default_sheet_name = "Tarifa"
