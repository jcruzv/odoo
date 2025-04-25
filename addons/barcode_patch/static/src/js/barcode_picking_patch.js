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
        console.log({result})
        // await this.save(); // Guardar después de procesar el código de barras
        return result;
    },
    async _processLocationDestination(barcodeData) {
        const configScanDest = this.config.restrict_scan_dest_location;
        if (configScanDest == "no") {
            return;
        }
        // For planned transfers, check the scanned location is a part of transfer destination.
        if (this._useReservation && !this._isSublocation(barcodeData.destLocation, this._defaultDestLocation())) {
            barcodeData.stopped = true;
            const message = _t("The scanned location doesn't belong to this operation's destination");
            return this.notification(message, { type: 'danger' });
        }

        const linea = this.selectedLine?.location_dest_id?.id || this.selectedPackageLine?.location_dest_id?.id
        
        if(linea != barcodeData.destLocation.id)
            if (!window.confirm("Estás seguro que quieres cambiar la ubicación de destino?")) {
                barcodeData.stopped = true;
                return;
            }

        // Change the destination of all concerned lines.
        const lines = this._getLinesToMove();
        for (const line of lines) {
            await this.changeDestinationLocation(barcodeData.destLocation.id, line);
        }
        barcodeData.stopped = true;
    },
});
