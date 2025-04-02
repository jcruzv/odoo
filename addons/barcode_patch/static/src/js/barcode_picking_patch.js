/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import BarcodePickingModel from "@stock_barcode/models/barcode_picking_model"; // Asegúrate de que esta ruta sea correcta y que el módulo esté presente
import { _t } from "@web/core/l10n/translation";

patch(BarcodePickingModel.prototype, {
    async _processBarcode(barcode) {
        if (this.isDone && !this.commands[barcode]) {
            return this.notification(_t("This picking is already done"), { type: "danger" });
        }
        const result = await super._processBarcode(barcode); // Usar super._processBarcode para llamar al método de la clase base

        // await this.save(); // Guardar después de procesar el código de barras
        return result;
    },
});
