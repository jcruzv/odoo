/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { _t } from "@web/core/l10n/translation";

patch(BarcodeModel.prototype, {
    async updateLotName(line, lotName) {
        // Checks if the tracking number isn't already used.
        for (const l of this.pageLines) {
            if (line.virtual_id === l.virtual_id ||
                line.product_id.tracking !== 'none' || line.product_id.id !== l.product_id.id) {
                continue;
            }
            if (lotName === l.lot_name || (l.lot_id && lotName === l.lot_id.name)) {
                this.notification(_t("This serial number is already used."), { type: "warning" });
                return;
            }
        }
        await this._updateLotName(line, lotName);
    },

    async _processBarcode(barcode) {
        console.log("Processing barcode", barcode);

        let barcodeData = {};
        let currentLine = false;
        const filters = {};

        if (this.selectedLine && this.selectedLine.product_id.tracking !== 'none') {
            filters['stock.lot'] = {
                product_id: this.selectedLine.product_id.id,
            };
        }

        filters['all'] = {
            company_id: [false].concat(this._getCompanyId() || []),
        };

        try {
            barcodeData = await this._parseBarcode(barcode, filters);
            if (this._shouldSearchForAnotherLot(barcodeData, filters)) {
                const lot = await this.cache.getRecordByBarcode(barcode, 'stock.lot');
                if (lot) {
                    Object.assign(barcodeData, { lot, match: true });
                }
            }
        } catch (parseErrorMessage) {
            barcodeData.error = parseErrorMessage;
        }

        this.scanHistory.unshift(barcodeData);

        if (barcodeData.match) {
            this.trigger('flash');
        }

        if (barcodeData.action) {
            return await barcodeData.action();
        }

        if (barcodeData.packaging) {
            Object.assign(barcodeData, this._retrievePackagingData(barcodeData));
        }

        const check = this._checkBarcode(barcodeData);
        if (check.error) {
            return this.notification(check.message, { title: check.title, type: "danger" });
        }

        if (barcodeData.product) {
            this.lastScanned.product = barcodeData.product;
        }

        if (barcodeData.lot && !barcodeData.product) {
            Object.assign(barcodeData, this._retrieveTrackingNumberInfo(barcodeData.lot));
        }

        await this._processLocation(barcodeData);
        await this._processPackage(barcodeData);
        if (barcodeData.stopped) {
            return;
        }

        if (barcodeData.weight) {
            barcodeData.quantity = barcodeData.weight.value;
        }

        if (!barcodeData.product) {
            return this.noProductToast(barcodeData);
        } else if (barcodeData.lot && barcodeData.lot.product_id !== barcodeData.product.id) {
            delete barcodeData.lot;
        }

        if (barcodeData.weight) {
            barcodeData.uom = this.cache.getRecord('uom.uom', barcodeData.product.uom_id);
        }

        if (!currentLine || this._shouldSearchForAnotherLine(currentLine, barcodeData)) {
            currentLine = this._findLine(barcodeData);
        }

        if (barcodeData.product.tracking === 'none' || barcodeData.lot || barcodeData.lotName || this._incrementTrackedLine()) {
            barcodeData.quantity = barcodeData.quantity || 1;
            if (barcodeData.product.tracking === 'serial' && barcodeData.quantity > 1) {
                barcodeData.quantity = 1;
                this.notification(
                    _t("A product tracked by serial numbers can't have multiple quantities for the same serial number."),
                    { type: 'danger' }
                );
            }
        }

        if (currentLine) {
            await this.updateLine(currentLine, this._convertDataToFieldsParams(barcodeData));
            this.trigger("playSound", "success");
        } else {
            currentLine = await this.createNewLine({ fieldsParams: this._convertDataToFieldsParams(barcodeData) });
            if (currentLine) {
                this.trigger("playSound", "success");
            }
        }

        if (currentLine) {
            this._selectLine(currentLine);
        }

        this.trigger('update');
        await this.save(); // Call save after processing the barcode
    },
});