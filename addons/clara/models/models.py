from odoo import models, fields, api

class clara(models.Model):
    _name = 'clara.move'
    _description = 'Transacciones de Clara Fintech'

    name = fields.Char(
        string='Nombre',
    )

    billing_statement_uuid = fields.Char(
        string='UUID del Estado de Cuenta',
    )
    billing_period_start_date = fields.Date(
        string='Fecha de Inicio del Periodo de Facturación',
    )
    billing_period_end_date = fields.Date(
        string='Fecha de Fin del Periodo de Facturación',
    )
    audit_accounting_date = fields.Date(
        string='Fecha de Contabilidad de Auditoría',
    )
    audit_operation_date = fields.Date(
        string='Fecha de Operación de Auditoría',
    )
    audit_last_update_date = fields.Date(
        string='Fecha de Última Actualización de Auditoría',
    )
    merchant_name = fields.Char(
        string='Nombre del Comerciante',
    )
    merchant_mcc = fields.Char(
        string='MCC del Comerciante',
    )
    merchant_description = fields.Text(
        string='Descripción del Comerciante',
    )
    merchant_category = fields.Char(
        string='Categoría del Comerciante',
    )
    merchant_category_code = fields.Char(
        string='Código de Categoría del Comerciante',
    )
    card_uuid = fields.Char(
        string='UUID de la Tarjeta',
    )
    card_masked_pan = fields.Char(
        string='PAN Enmascarado de la Tarjeta',
    )
    user_uuid = fields.Char(
        string='UUID del Usuario',
    )
    user_holder_name = fields.Char(
        string='Nombre del Titular del Usuario',
    )
    original_amount_currency = fields.Char(
        string='Moneda del Monto Original',
    )
    original_amount_value = fields.Float(
        string='Valor del Monto Original',
    )
    amount_value_currency = fields.Char(
        string='Moneda del Valor del Monto',
    )
    amount_value_amount = fields.Float(
        string='Cantidad del Valor del Monto',
    )
    validation_status = fields.Char(
        string='Estado de Validación',
    )
    validation_comment = fields.Text(
        string='Comentario de Validación',
    )
    has_invoice = fields.Boolean(
        string='Tiene Factura',
    )
    has_attachments = fields.Boolean(
        string='Tiene Adjuntos',
    )
    bank_concept_number = fields.Char(
        string='Número de Concepto Bancario',
    )
    bank_concept_description = fields.Text(
        string='Descripción de Concepto Bancario',
    )

    description = fields.Text(
        string='Descripción',
    )

    uuid = fields.Char(
        string='UUID',
    )

    type = fields.Char(
        string='Tipo',
    )

    transaction_label = fields.Char(
        string='Etiqueta de Transacción',
    )

    status = fields.Char(
        string='Estado',
    )

    comment = fields.Text(
        string='Comentario',
    )

    authorization_number = fields.Char(
        string='Número de Autorización',
    )

    installment = fields.Char(
        string='Cuota',
    )

    installment_number = fields.Char(
        string='Número de Cuota',
    )