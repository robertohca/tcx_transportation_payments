from odoo import api, fields, models
from odoo.addons.model_basic_ops_notifications.models.mixin import (
    depends_and_suppress_notifications,
    onchange_and_suppress_notifications,
)
from odoo.addons.tecnotex.fields import (
    TcxCharField,
    TcxFloatField,
    TcxIntegerField,
    TcxMany2many,
    TcxOne2many,
    TcxTextField,
)
from odoo.addons.tecnotex_servicio_pago_transporte.models.nomenclador import (
    TIPO_DE_CONTENEDOR_MODEL_NAME,
    LUGAR_ORIGEN_DESTINO_MODEL_NAME,
)
from odoo.addons.tecnotex_servicio_pago_transporte.models.tarifa_transportista import (
    TARIFA_TRANSPORTISTA_MODEL_NAME,
)
from odoo.addons.utils.regex import (
    CAPITALIZED_LETTERS_AND_SPACES_REGEX,
    CAPITALIZED_LETTERS_NUMBERS_AND_SPACES_REGEX,
    LETTERS_NUMBERS_SPACES_AND_SPECIALS2_REGEX,
)
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError

CARTA_PORTE_MODEL_NAME = "carta.porte"
PAGO_TRANSPORTE_MODEL_NAME = "pago.transporte"


class Cartas_Porte(models.Model):
    _name = CARTA_PORTE_MODEL_NAME
    _description = "Listado de Cartas de Porte"
    _rec_name = ""

    carta_table_id = fields.Many2one(PAGO_TRANSPORTE_MODEL_NAME)

    id_spt = TcxIntegerField("Id SPT", required=True)
    id_spago = TcxIntegerField("Id SPago", required=True)
    id_carta_Porte = TcxIntegerField("Id Carta de Porte")
    id_caratula = TcxIntegerField("Id de Carátula")
    id_contrato = TcxIntegerField("Id de Contrato")
    importe_carta = fields.Monetary(string="Importe", compute="_compute_importe_carta")
    currency_id = fields.Many2one("res.currency", related="carta_table_id.currency_id")
    tipo_contenedor_id = fields.Many2one(
        TIPO_DE_CONTENEDOR_MODEL_NAME, "Tipo de Contenedor", required=True
    )
    origen = fields.Many2one(LUGAR_ORIGEN_DESTINO_MODEL_NAME, "Origen", required=True)
    destino = fields.Many2one(LUGAR_ORIGEN_DESTINO_MODEL_NAME, "Destino", required=True)
    contratos_ids = fields.One2many(
        "tcx_carta.contrato.rel", "carta_id", string="Contratos"
    )

    @api.onchange("origen", "destino")
    def validar_locaciones(self):

        if self.origen and self.destino:
            if self.origen == self.destino:
                raise ValidationError(
                    "El lugar de origen y destino de la mercancía no puede ser el mismo."
                )

    @depends_and_suppress_notifications("tipo_contenedor_id", "origen", "destino")
    def _compute_importe_carta(self):
        for carta in self:
            result = (
                self.env[TARIFA_TRANSPORTISTA_MODEL_NAME]
                .sudo()
                .search(
                    [
                        "&",
                        "&",
                        ("tipo_contenedor", "=", carta.tipo_contenedor_id.denominacion),
                        ("origen", "=", carta.origen.denominacion),
                        ("destino", "=", carta.destino.denominacion),
                    ]
                )
            )
            if result:
                carta.importe_carta = result.precio_km_ton
            else:
                carta.importe_carta = 0.00

    @api.model
    def create(self, vals):

        if not vals.get("contratos_ids", False):
            raise ValidationError(
                "Debe agregar al menos un contrato a la carta de porte."
            )

        return super(Cartas_Porte, self).create(vals)

    def write(self, vals):

        if not vals.get("contratos_ids", False):
            raise ValidationError(
                "Debe agregar al menos un contrato a la carta de porte."
            )

        return super(Cartas_Porte, self).write(vals)
