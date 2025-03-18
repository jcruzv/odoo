/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { _t } from "@web/core/l10n/translation";
import { BarcodeObject } from "@stock_barcode/barcode_object";

console.log(BarcodeObject)

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

        const loadLot = async (lote) => {
            console.log("loadLote", lote);
            const records = await this.orm.searchRead("stock.lot", [["display_name", "=", lote]], ["id"]);
            console.log(records);
            if (records.length > 0) {
                return records[0];
            }
        }

        const loadRecord = async (lot_id) => {

            console.log("buscando record", lot_id)
            
            // obentener el id del stock.move.line, primero obteniendo el stock.move desde el stock.picking

            console.log("args", [["picking_id", "=", this.resId]])
            
            const records = await this.orm.searchRead("stock.move", [["picking_id", "=", this.resId]], ["id"]);
            console.log(records);

            const moves = records.map(x=>x.id)
            
            const records2 = await this.orm.searchRead("stock.move.line", [["move_id", "in", moves], ["lot_id", "=", lot_id]], ["id"]);
            console.log(records2);
            if (records2.length > 0) {
                return records2[0];
            }
        }

        const updateRecord = async (id) => {

            console.log("actualizar record:" + id);

            const producto = await this.orm.searchRead("stock.move.line", [["id", "=", id]], ["id", "product_id"]);

            console.log({producto});
            
            const embalaje = await this.orm.searchRead("product.packaging", [["product_id", "=", producto[0].product_id[0]]], ["qty"]);
            
            console.log({embalaje});
            
            await this.orm.write("stock.move.line", [id], { quantity: embalaje[0].qty });
        
            // Opcional: Volver a cargar el registro para reflejar los cambios
            // await this.loadRecord();
        }

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

        // Add filter to search in "lotes"
        filters['stock.lot'] = {
            barcode: barcode,
        };

        try {
            barcodeData = await this._parseBarcode(barcode, filters);
            if(this._shouldSearchForAnotherLot(barcodeData, filters)){
                const lot = await this.cache.getRecordByBarcode(barcode, 'stock.lot');
                console.log({lot});
                if (lot) {
                    Object.assign(barcodeData, { lot, match: true });
                }
            }
        } catch (parseErrorMessage) {
            barcodeData.error = parseErrorMessage;
        }

        this.scanHistory.unshift(barcodeData);

        if (this.cache.dbIdCache["stock.picking"][this.resId].partner_id == 260) {
            this.trigger('flash');

            const lot = await loadLot(barcode)

            console.log({lot})
            
            const rec = await loadRecord(lot.id);

            console.log({rec})

            const actualizar = await updateRecord(rec.id);

        }
        
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

    splitBarcode(barcode) {
        console.log("barcode", barcode);
        // If the barcode has multiple URI, separate them.
        const matchedURI = [...barcode.matchAll(/urn:(?:[a-z0-9 -]+:){3} ?[0-9.]+/g)];
        if (matchedURI.length > 1) {
            return matchedURI.map(uri => uri[0]);
        }
        // If the barcode contains the separator, split it.
        const sepRegex = RegExp(this.config.barcode_separator_regex);
        const splitBarcodes = barcode.split(sepRegex).filter(bc => bc);
        if (splitBarcodes.length > 1) {
            return [...splitBarcodes];
        }
        return [barcode];
    },
    
    async processBarcode(barcode, options={}) {
        console.log({barcode});
        if (!barcode) {
            return; // Do nothing if no barcode given.
        }
        const { readingRFID } = options;
        const barcodes = this.splitBarcode(barcode);
        if (barcodes.length > 1 && barcode === this._currentBarcode) {
            // Scanning multiple barcodes at once can take some time and the user may be
            // tempted to scan again, thinking that the barcodes weren't scanned.
            // To avoid processing the same group of barcodes multiple times, we keep the
            // last scanned group of barcodes in memory and nothing will be done if the barcode
            // is scanned again while previous one is still in process.
            return;
        }
        this._currentBarcode = barcode;

        // Filters out already scanned URI.
        const filteredBarcodes = [];
        for (const bc of barcodes) {
            const matchedURI = bc.match(/^urn:.*$/);
            if (matchedURI && this.uriInCache(matchedURI[0])) {
                continue;
            }
            filteredBarcodes.push(bc);
        }

        if (barcodes.length > 1 && !readingRFID) {
            this.trigger("addBarcodesCountToProcess", filteredBarcodes.length)
        }
        // Parse all barcodes.
        const parsedBarcodes = [];
        for (const bc of filteredBarcodes) {
            const barcodeObject = BarcodeObject.forBarcode(bc);
            await barcodeObject.setRecords();
            parsedBarcodes.push(barcodeObject);
        }
        // Fetch all needed missing data and add them to the cache.
        await this._getMissingRecords();

        // Link parsed barcodes with missing information to the corresponding record(s).
        const validBarcodes = [];
        for (const barcodeObject of parsedBarcodes) {
            if (barcodeObject.hasMissingRecords) {
                await barcodeObject.setRecords();
                if (barcodeObject.isURN && barcodeObject.hasMissingRecords &&
                    barcodeObject.missingRecords.find(mr => mr.type === "product")) {
                    // This barcode is linked to a product we don't have => We ignore it.
                    // TODO: what to do with those barcodes ? Missing product => Barcode Lookup ?
                    // TODO: already scanned SN should be managed here too ?
                    this.trigger("updateBarcodesCountProcessed");
                    continue;
                }
            }
            validBarcodes.push(barcodeObject);
        }

        this.actionMutex.exec(async () => {
            for (const barcodeObject of validBarcodes) {
                // TODO: use already parsed barcode in `_processBarcode` instead of parse it again.
                await this._processBarcode(barcodeObject.rawValue);
                this.trigger("updateBarcodesCountProcessed");
            }
        });
        this.postProcessBarcode();
    }
    
    
});
