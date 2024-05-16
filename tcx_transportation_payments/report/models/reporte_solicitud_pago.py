from odoo import fields, models, api


class ReporteSolicitud(models.TransientModel):
    _name = "reporte.solicitud"
    _description = "Asistente para generar el reporte de solicitudes de pago."

    a_favor_reporte = fields.Many2one("transportista", "A Favor De", required=True)

    def generate_report_pi(self):

        seleccion = (
            self.env["pago.transporte"]
            .search([])
            .filtered(lambda sp: sp.a_favor == self.a_favor_reporte)
        )

        total_pi = len(seleccion)
        plan_importe_total = 0
        fecha_impresion = fields.Date.today()
        emitido_por = self.env.user.name

        for sp in seleccion:
            plan_importe_total += sp.importe

        data = {
            "a_favor_reporte_d": self.a_favor_reporte.nombre_transp,
            "total_pi_d": total_pi,
            "plan_importe_total_d": plan_importe_total,
            "fecha_impresion_d": fecha_impresion,
            "emitido_por_d": emitido_por,
            "elem": [
                {
                    "seleccion_pi_d": seleccion.mapped(
                        lambda sp: dict(
                            num_solicitud=sp.num_solicitud,
                            num_factura=sp.num_factura,
                            importe_total=sp.importe,
                        )
                    )
                }
            ],
        }
        return self.env.ref(
            "tecnotex_servicio_pago_transporte.reporte_solicitud_pago"
        ).report_action([], data=data)

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env["pago.transporte"].browse(docids)
        lines = []
        for line in docs.carta_ids:  # select the One2many field you want to use
            # do some data processing here
            lines.append(
                {
                    "num_contrato": line.num_contrato or "",
                    "id_spt": line.id_spt or 0,
                    "importe_carta": line.importe_carta or 0.0,
                }
            )
        return self.env.ref(
            "tecnotex_servicio_pago_transporte.reporte_solicitud_pago"
        ).report_action(docids, data=data, config=False)
