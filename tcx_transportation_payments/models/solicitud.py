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
from odoo.addons.tecnotex_servicio_pago_transporte.models.transportista import (
    TRANSPORTISTA_MODEL_NAME,
)
from odoo.addons.tecnotex_servicio_pago_transporte.models.carta_porte import (
    CARTA_PORTE_MODEL_NAME,
)
from odoo.exceptions import ValidationError, UserError

from datetime import datetime

ESTADO_PENDIENTE = "Pendiente"
ESTADO_ENVIADO_AL_PAGO = "Enviada a Finanzas"
ESTADO_A_PAGADO = "Enviada al Pago"
ESTADO_PAGADO = "Pagada"
ESTADO_RECHAZADO = "Rechazada"

ESTADO_SOLICITUD_PAGO_TRANSPORTE_SELECTION = [
    (ESTADO_PENDIENTE, ESTADO_PENDIENTE),
    (ESTADO_ENVIADO_AL_PAGO, ESTADO_ENVIADO_AL_PAGO),
    (ESTADO_A_PAGADO, ESTADO_A_PAGADO),
    (ESTADO_PAGADO, ESTADO_PAGADO),
    (ESTADO_RECHAZADO, ESTADO_RECHAZADO),
]

PAGO_TRANSPORTE_MODEL_NAME = "pago.transporte"

REQUEST_STATES_DICT = dict(ESTADO_SOLICITUD_PAGO_TRANSPORTE_SELECTION)


class Solicitud(models.Model):
    _name = PAGO_TRANSPORTE_MODEL_NAME
    _description = "Listado de solicitudes"
    _rec_name = "num_solicitud"

    num_solicitud = fields.Char("Número de solicitud", readonly=True)
    num_factura = TcxIntegerField("Número de Factura", required=True)
    importe = fields.Monetary(
        string="Importe", readonly=True, compute="_compute_amount_total"
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env["res.currency"]
        .search([("name", "=", "CUP")], limit=1)
        .id,
    )

    a_favor = fields.Many2one(
        TRANSPORTISTA_MODEL_NAME, string="A Favor De", required=True
    )

    fecha_entrada = fields.Date(
        string="Fecha de entrada en Tecnotex",
        default=fields.Date.context_today,
        required=True,
    )
    fecha_confeccion = fields.Date(
        string="Fecha presentado",
        readonly=True,
        default=fields.Date.context_today,
        required=True,
    )

    carta_ids = TcxOne2many(
        CARTA_PORTE_MODEL_NAME, "carta_table_id", string="Cartas de Porte Asociadas"
    )

    estado_solicitud = fields.Selection(
        ESTADO_SOLICITUD_PAGO_TRANSPORTE_SELECTION,
        default=ESTADO_PENDIENTE,
        required=True,
    )
    state = fields.Char(compute="_compute_from_estado")

    observaciones_solicitud = fields.Text("Observaciones")

    contract_count = fields.Integer(
        compute="_compute_count_contracts", string="Contract Count"
    )

    historico = fields.One2many(
        "historico.estados", "solicitud_id", "Histórico de Estados"
    )

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super().fields_get(allfields, attributes)
        hide_list = ["create_uid", "create_date", "write_uid", "write_date"]
        for field in hide_list:
            if res.get(field):
                res[field]["searchable"] = False
        return res

    @api.depends("contract_count")
    def _compute_count_contracts(self):
        for record in self:
            contracts = self.env[CARTA_PORTE_MODEL_NAME].search(
                [("carta_table_id", "=", self.id)]
            )
            distinct_contracts = list(
                set(contracts.mapped("contratos_ids.contrato_id.numero_contrato"))
            )
            record.contract_count = len(distinct_contracts)

    def return_action_to_open(self):
        """This opens the xml view specified in xml_id for the current vehicle"""
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"]._for_xml_id(
                "tecnotex_contratacion.%s" % xml_id
            )
            res.update(
                context=dict(
                    self.env.context, default_numero_contrato=self.id, group_by=False
                ),
                domain=[
                    (
                        "numero_contrato",
                        "=",
                        self.carta_ids.contratos_ids.contrato_id.mapped(
                            "numero_contrato"
                        ),
                    )
                ],
            )
            return res
        return False

    @depends_and_suppress_notifications("estado_solicitud")
    def _compute_from_estado(self):
        for solicitud in self:
            solicitud.state = solicitud.estado_solicitud

    def solicitud_pendiente(self):
        for recs in self:
            if recs.estado_solicitud != ESTADO_PENDIENTE:
                recs.write({"estado_solicitud": ESTADO_PENDIENTE})

    def solicitud_enviada_pago(self):
        for recs in self:
            if recs.estado_solicitud != ESTADO_ENVIADO_AL_PAGO:
                recs.write({"estado_solicitud": ESTADO_ENVIADO_AL_PAGO})

    def solicitud_pagada(self):
        for recs in self:
            if recs.estado_solicitud != ESTADO_A_PAGADO:
                recs.write({"estado_solicitud": ESTADO_A_PAGADO})

    def solicitud_rechazar(self):
        for recs in self:
            if recs.estado_solicitud != ESTADO_PAGADO:
                recs.write({"estado_solicitud": ESTADO_RECHAZADO})

    def solicitud_pagar(self):
        for recs in self:
            if recs.estado_solicitud != ESTADO_PAGADO:
                recs.write({"estado_solicitud": ESTADO_PAGADO})

    def _create_historical_record(self, estado_solicitud, observaciones_solicitud):
        """
        Create a new historical record every time the state is changed
        """
        user_id = self.env.user
        user = self.env["res.users"].sudo().search([("id", "=", int(user_id))])
        if not user:
            user = "OdooBot"
        else:
            user = user.name

        self.ensure_one()
        self.env["historico.estados"].create(
            {
                "solicitud_id": self.id,
                "state": estado_solicitud,
                "user": user,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "observation": observaciones_solicitud,
            }
        )

    @api.model
    def create(self, vals):
        seq = (
            str("TCX_SPT_")
            + str(fields.Date.today().year)
            + self.env["ir.sequence"].next_by_code("pago_transporte_seq")
            or "/"
        )
        vals["num_solicitud"] = seq
        vals["estado_solicitud"] = "Pendiente"

        if not vals.get("carta_ids", False):
            raise ValidationError(
                "Debe agregar al menos una carta de porte a la solicitud."
            )

        res = super(Solicitud, self).create(vals)

        user_id = self.env.user
        fdate = datetime.now()
        user = self.env["res.users"].sudo().search([("id", "=", int(user_id))])
        if not user:
            user = "OdooBot"
        else:
            user = user.name

        self.env["historico.estados"].create(
            {
                "solicitud_id": res.id,
                "state": "Pendiente",
                "user": user,
                "date": fdate.date(),
                "observation": self.observaciones_solicitud,
            }
        )

        return res

    def write(self, vals):

        if self.estado_solicitud == "Pagada":
            # Or any other error message you want to display.
            raise ValidationError(
                "La edición de registros no está permitida en ese estado. (Solicitud Pagada)"
            )

        self._create_historical_record(
            vals.get("estado_solicitud") or self.estado_solicitud,
            vals.get("observaciones_solicitud") or self.observaciones_solicitud,
        )

        return super(Solicitud, self).write(vals)

    def generate_report_pi(self):
        seleccion = self.carta_ids
        a_favor = self.a_favor
        total_cartas = len(seleccion)
        importe_cartas_total = sum(seleccion.mapped("importe_carta"))
        fecha_impresion = fields.Date.today()
        emitido_por = self.env.user.name

        data = {
            "a_favor_d": a_favor.nombre_transp,
            "total_cartas_d": total_cartas,
            "importe_cartas_total_d": importe_cartas_total,
            "fecha_impresion_d": fecha_impresion,
            "emitido_por_d": emitido_por,
            "elem": [
                {
                    "seleccion_cartas_d": seleccion.mapped(
                        lambda c: dict(
                            id_spt=c.id_spt,
                            id_spago=c.id_spago,
                            num_contrato=c.contratos_ids.contrato_id.numero_contrato,
                            importe_carta=c.importe_carta,
                            id_contrato=c.id_contrato,
                        )
                    )
                }
            ],
        }
        return self.env.ref(
            "tecnotex_servicio_pago_transporte.reporte_solicitud_pago"
        ).report_action([], data=data)

    @api.depends("carta_ids.importe_carta")
    def _compute_amount_total(self):
        for records in self:
            records.importe = sum(
                importe.importe_carta for importe in records.carta_ids
            )

    @api.onchange("fecha_entrada", "fecha_confeccion")
    def _check_fecha(self):
        if self.fecha_entrada and self.fecha_confeccion:
            if self.fecha_entrada < self.fecha_confeccion:
                self.fecha_entrada = self.fecha_confeccion
                raise ValidationError(
                    "La fecha de entrada en TECNOTEX no puede ser anterior a la fecha de presentada la solicitud."
                )
