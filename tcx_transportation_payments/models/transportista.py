from odoo import api, fields, models
from odoo.addons.model_basic_ops_notifications.models.mixin import (
    depends_and_suppress_notifications,
    onchange_and_suppress_notifications,
)
from odoo.addons.modify_model_from_excel_file.models.modify_model_from_excel_file import (
    FROM_EXCEL_FILE_MIXIN_MODEL_NAME,
)
from odoo.addons.tecnotex.fields import (
    TcxCharField,
    TcxFloatField,
    TcxIntegerField,
    TcxMany2many,
    TcxOne2many,
    TcxTextField,
)
from odoo.addons.tecnotex.models.comun import (
    WITH_ADDRESS_MIXIN_MODEL_NAME,
    WITH_CONTACT_INFO_MIXIN_MODEL_NAME,
)
from odoo.addons.tecnotex.models.nomenclador import (
    BENEFICIARIO_MODEL_NAME,
    REPRESENTANTE_MODEL_NAME,
)
from odoo.addons.tecnotex_mercado.models.comun import COMMON_TO_MARKET_MODULE_MODEL_NAME
from odoo.addons.tecnotex_mercado.models.nomenclador import (
    ACREDITACION_EN_CUBA_MODEL_NAME,
)
from odoo.addons.utils.regex import (
    CAPITALIZED_LETTERS_AND_SPACES_REGEX,
    CAPITALIZED_LETTERS_NUMBERS_AND_SPACES_REGEX,
    LETTERS_NUMBERS_SPACES_AND_SPECIALS2_REGEX,
)
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError

DEL = [("Cubanos", "Cubanos"), ("Extranjeros", "Extranjeros"), ("MINFAR", "MINFAR")]
REPRE_TIPO_TRANSPORTISTA = "Transportista"

TRANSPORTISTA_MODEL_NAME = "transportista"
OFICINA_TRANSPORTISTA_MODEL_NAME = "oficina.transportista"
REPRE_TRANSPORTISTA_MODEL_NAME = "representante.transportista"
BEN_TRANSPORTISTA_MODEL_NAME = "beneficiario.transportista"
TARIFA_TRANSPORTISTA_MODEL_NAME = "tarifa.transportista"


class Transportista(models.Model):
    _inherit = [
        COMMON_TO_MARKET_MODULE_MODEL_NAME,
        WITH_ADDRESS_MIXIN_MODEL_NAME,
        WITH_CONTACT_INFO_MIXIN_MODEL_NAME,
    ]
    _name = TRANSPORTISTA_MODEL_NAME
    _description = "Listado de Transportistas"
    _rec_name = "nombre_transp"

    nombre_transp = TcxCharField(
        "Nombre del Transportista",
        required=True,
        regex=LETTERS_NUMBERS_SPACES_AND_SPECIALS2_REGEX,
    )
    codigo = TcxIntegerField("Código", required=True)
    direccion = fields.Selection(DEL, "DEL")

    oficinas_en_cuba_ids = TcxOne2many(
        OFICINA_TRANSPORTISTA_MODEL_NAME, "proveedor_id", string="Oficina en Cuba"
    )
    representantes_ids = TcxOne2many(
        REPRE_TRANSPORTISTA_MODEL_NAME, "proveedor_id", string="Representantes"
    )

    selected_repres = fields.One2many(
        # Para ser utilizado como parte del dominio del campo "Representante"
        # que se encuentra en la relación `representantes_ids`.
        REPRESENTANTE_MODEL_NAME,
        "proveedor_id",
    )
    beneficiarios_ids = TcxOne2many(
        BEN_TRANSPORTISTA_MODEL_NAME, "proveedor_id", string="Beneficiarios"
    )
    selected_benes = fields.One2many(
        # Para ser utilizado como parte del dominio del campo "Beneficiario"
        # que se encuentra en la relación `beneficiarios_ids`.
        BENEFICIARIO_MODEL_NAME,
        "proveedor_id",
    )

    tarifa_id = TcxOne2many(TARIFA_TRANSPORTISTA_MODEL_NAME, TRANSPORTISTA_MODEL_NAME)
    observaciones = TcxCharField("Observaciones")

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        hide_list = [
            "create_uid",
            "create_date",
            "write_uid",
            "write_date",
            "address_fields_holder",
            "clear_related_relations",
            "show_email_fields_from_mixin",
            "contact_info_fields_holder",
            "preview_file_content",
            "import_file",
            "import_template_id",
            "id",
            "selected_repres",
            "selected_benes",
            "paginaweb_readonly",
            "paginaweb",
            "fax",
            "fax_readonly",
            "correo",
            "correo_readonly",
            "entre_calles",
            "pais",
        ]
        for field in hide_list:
            if res.get(field):
                res[field]["searchable"] = False
        return res


class TransportistaOficinaEnCuba(models.Model):
    _inherit = [
        COMMON_TO_MARKET_MODULE_MODEL_NAME,
        WITH_ADDRESS_MIXIN_MODEL_NAME,
        WITH_CONTACT_INFO_MIXIN_MODEL_NAME,
    ]
    _name = OFICINA_TRANSPORTISTA_MODEL_NAME
    _description = "Oficina en Cuba relacionada con el proveedor"
    _rec_name = "vendedor_oficina_cuba"
    _do_case_insensitive_check = False

    proveedor_id = fields.Many2one(
        TRANSPORTISTA_MODEL_NAME, required=True, ondelete="cascade"
    )
    vendedor_oficina_cuba = TcxCharField("Vendedor")
    cargo_oficina_cuba = TcxCharField("Cargo")
    correo_oficina_cuba = fields.Char("Correo")
    acreditacion_en_Cuba_oficina_cuba = fields.Many2one(
        ACREDITACION_EN_CUBA_MODEL_NAME,
        string="Acreditación en Cuba",
        help="Acreditación en Cuba",
        required=True,
        ondelete="cascade",
    )
    fecha_de_vencimiento_oficina_cuba = fields.Date("Fecha de vencimiento")
    show_email_fields_from_mixin = fields.Boolean(default=False)

    # Datos de contacto (que deben ser obligatorios...)
    calle_nro = TcxCharField(required=True)
    pais = fields.Many2one(required=True)
    contacto_pais = fields.Many2one(required=True)
    telefono = TcxIntegerField(required=True)


class HerRepresentante(models.Model):
    _inherit = REPRESENTANTE_MODEL_NAME

    proveedor_id = fields.Many2one("tranportista")
    # Extendiendo los "tipos de representates"...
    tipo_representante = fields.Selection(
        selection_add=[("Transportista", "Transportista")],
        ondelete={"Transportista": "cascade"},
    )


class RepresentanteTransportista(models.Model):
    _name = REPRE_TRANSPORTISTA_MODEL_NAME

    representante_id = fields.Many2one(
        REPRESENTANTE_MODEL_NAME,
        required=True,
        ondelete="cascade",
        # De esta forma podemos hacer referencia a un campo del "widget padre",
        # que en este caso serían los datos del modelo "Proveedor".
        domain=f"[('id', 'not in', parent.selected_repres), ('tipo_representante', '=', '{REPRE_TIPO_TRANSPORTISTA}')]",
        context={
            "hide_tipo_representante": True,
            "default_tipo_representante": REPRE_TIPO_TRANSPORTISTA,
        },
    )
    proveedor_id = fields.Many2one(TRANSPORTISTA_MODEL_NAME, ondelete="cascade")
    active_prov = fields.Boolean("¿Activo para este proveedor?")
    resumen = fields.Char("Dirección", related="representante_id.resumen")
    correo_readonly = fields.Char(
        "Correo electrónico", related="representante_id.correo_readonly"
    )
    telefono_readonly = fields.Char(
        "Teléfono", related="representante_id.telefono_readonly"
    )


class Beneficiario(models.Model):
    _inherit = BENEFICIARIO_MODEL_NAME

    proveedor_id = fields.Many2one(TRANSPORTISTA_MODEL_NAME)


class BeneficiarioTransportista(models.Model):
    _name = BEN_TRANSPORTISTA_MODEL_NAME

    beneficiario_id = fields.Many2one(
        BENEFICIARIO_MODEL_NAME,
        required=True,
        ondelete="cascade",
        # De esta forma podemos hacer referencia a un campo del "widget padre",
        # que en este caso serían los datos del modelo "Proveedor".
        domain="[('id', 'not in', parent.selected_benes)]",
    )
    proveedor_id = fields.Many2one(TRANSPORTISTA_MODEL_NAME, ondelete="cascade")
    active_prov = fields.Boolean("¿Activo para este proveedor?")
    resumen = fields.Char("Dirección", related="beneficiario_id.resumen")
    fecha_inicio = fields.Date("Fecha inicio", related="beneficiario_id.fecha_inicio")
    fecha_fin = fields.Date("Fecha fin", related="beneficiario_id.fecha_fin")
    excepcional_repr = fields.Char(
        "¿Es excepcional?", related="beneficiario_id.excepcional_repr"
    )
