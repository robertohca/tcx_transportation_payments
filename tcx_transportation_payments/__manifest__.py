# -*- coding: utf-8 -*-
{
    "name": "Tecnotex Pagos de Servicios de Transporte",
    "summary": """Módulo para la gestión del proceso de Pagos de Servicios de Transporte""",
    "description": """Módulo para la gestión del proceso de Pagos de Servicios de Transporte""",
    "author": "CEIGE AGE TEAM, Roberto Camejo",
    "website": "http://github.com/robertohca",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "1.0",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "tecnotex",
        "uom",
        "tecnotex_contratacion",
        "tecnotex_economia",
    ],
    # always loaded
    "data": [
        "views/tecnotex_pago_transporte_principal.xml",
        "views/menu.xml",
        "views/tecnotex_carta_porte.xml",
        "views/tecnotex_transportista.xml",
        "views/tecnotex_excel_transportista.xml",
        "views/nomencladores/nom_tipo_contenedor_view.xml",
        "views/nomencladores/nom_lugar_origen.xml",
        "data/secuencia.xml",
        "data/acciones.xml",
        "data/tipo_contenedores.xml",
        "data/puertos.xml",
        "report/wizard/reporte_solicitud_pago_view.xml",
        "report/templates/reporte_solicitud_pago_view.xml",
    ],
    # demo
    "demo": [],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
