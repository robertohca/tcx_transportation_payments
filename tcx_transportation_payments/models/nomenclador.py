from odoo import api, fields, models
from odoo.addons.model_basic_ops_notifications.models.mixin import (
    depends_and_suppress_notifications,
    onchange_and_suppress_notifications,
)
from odoo.addons.tecnotex.fields import (
    TcxCharField,
    TcxFloatField,
    TcxIntegerField,
    TcxOne2many,
    TcxTextField,
)
from odoo.addons.tecnotex.models.comun import (
    FEMALE_SELECTED_REPR,
    MALE_SELECTED_REPR,
    NOMENCLATOR_WITH_STATE_MIXIN_MODEL_NAME,
    PAIS_MODEL_NAME,
)
from odoo.addons.utils.regex import (
    LETTERS_AND_SPACES_REGEX,
    LETTERS_NUMBERS_AND_SPACES_REGEX,
    LETTERS_NUMBERS_SPACES_AND_SPECIALS_REGEX,
    LETTERS_REGEX,
    NON_ZERO_REGEX,
    NUMBER_REGEX,
)

TIPO_DE_CONTENEDOR_MODEL_NAME = "tipo.contenedor"
LUGAR_ORIGEN_DESTINO_MODEL_NAME = "lugar.origen.destino"


class TipoDeOperacion(models.Model):
    _inherit = [NOMENCLATOR_WITH_STATE_MIXIN_MODEL_NAME]
    _name = TIPO_DE_CONTENEDOR_MODEL_NAME
    _description = "Nomenclador de los tipos de contenedores."

    denominacion = fields.Char(size=100, required=True)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        hide_list = ["create_uid", "create_date", "write_uid", "write_date"]
        for field in hide_list:
            if res.get(field):
                res[field]["searchable"] = False
        return res


class Puertos(models.Model):
    _inherit = [NOMENCLATOR_WITH_STATE_MIXIN_MODEL_NAME]
    _name = LUGAR_ORIGEN_DESTINO_MODEL_NAME
    _description = "Nomenclador de los lugares de origen y destino."

    denominacion = TcxCharField(size=100, required=True, regex=LETTERS_AND_SPACES_REGEX)

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        hide_list = ["create_uid", "create_date", "write_uid", "write_date"]
        for field in hide_list:
            if res.get(field):
                res[field]["searchable"] = False
        return res
