/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { _t } from "@web/core/l10n/translation";
import { BarcodeObject } from "@stock_barcode/barcode_object";

console.log("TEST", BarcodeObject)

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

            const records = await this.orm.searchRead("stock.move", [["picking_id", "=", this.resId]], ["id", "product_id", "display_name"]);
            console.log(records);

            const products = records.map(x=>x.product_id[0])
            
            //console.log("loadLote", lote);

            console.log("args lote:", [["display_name", "=", lote], ["product_id", "in", products]]);
            
            const lotes = await this.orm.searchRead("stock.lot", [["display_name", "=", lote], ["product_id", "in", products]], ["id", "product_id", "display_name"]);
            console.log(lotes);
            if (lotes.length > 0) {
                return lotes[0];
            }
        }

        const loadProduct = async (product) => {

            const records = await this.orm.searchRead("product.product", [["id", "=", product]], ["id", "barcode", "categ_id", "code", "default_code", "display_name", "has_image", "is_storable", "tracking", "uom_id", "use_time"]);
            console.log(records);

            //console.log(lotes);
            if (records.length > 0) {
                return records[0];
            }
        }

        const loadRecord = async (lot_id) => {

            //console.log("buscando record", lot_id)
            
            // obentener el id del stock.move.line, primero obteniendo el stock.move desde el stock.picking

            //console.log("args", [["picking_id", "=", this.resId]])
            
            const records = await this.orm.searchRead("stock.move", [["picking_id", "=", this.resId]], ["id"]);
            //console.log(records);

            const moves = records.map(x=>x.id)

            //console.log("args line", [["move_id", "in", moves], ["lot_id", "=", lot_id]]);
            
            const records2 = await this.orm.searchRead("stock.move.line", [["move_id", "in", moves], ["lot_id", "=", lot_id]], ["id"]);
            //console.log(records2);
            if (records2.length > 0) {
                return records2[0];
            }
        }

        const updateRecord = async (id) => {

            //console.log("actualizar record:" + id);

            const producto = await this.orm.searchRead("stock.move.line", [["id", "=", id]], ["id", "product_id"]);

            console.log({producto});
            
            const embalaje = await this.orm.searchRead("product.packaging", [["product_id", "=", producto[0].product_id[0]]], ["qty"]);
            
            //console.log({embalaje});
            
            await this.orm.write("stock.move.line", [id], { quantity: embalaje[0].qty });

            return embalaje[0];
            // Opcional: Volver a cargar el registro para reflejar los cambios
            // await this.loadRecord();
        }
        
        const getPackage = async (id) => {
            if(!id)
                return false;
            //console.log("actualizar record:" + id);
            
            const embalaje = await this.orm.searchRead("product.packaging", [["product_id", "=", id]], ["qty"]);

            console.log(embalaje)
            
            if(embalaje.length!=0)
                return embalaje[0]?.qty || 1;
            else
                return false;
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
        
        // if (this.cache.dbIdCache["stock.picking"][this.resId].partner_id == 260) {
        //     filters['stock.lot'] = {
        //         barcode: barcode,
        //     };
        // }

        try {
            barcodeData = await this._parseBarcode(barcode, filters);
            console.log("first", {barcodeData});
            if(this._shouldSearchForAnotherLot(barcodeData, filters)){
                const lot = await this.cache.getRecordByBarcode(barcode, 'stock.lot');
                //console.log({lot});
                if (lot) {
                    Object.assign(barcodeData, { lot, match: true });
                }
            }
        } catch (parseErrorMessage) {
            barcodeData.error = parseErrorMessage;
        }

        console.log(this)
        
        console.log({barcodeData});
        console.log({"DATA": JSON.stringify(barcodeData)});

        this.scanHistory.unshift(barcodeData);
            
        if (this.cache.dbIdCache["stock.picking"][this.resId].partner_id == 260 &&
               (
                   barcodeData.error || 
                   (barcodeData.lotName && barcodeData.lotName !== null) ||
                   (barcodeData.lot && barcodeData.lot !== null)
               )
           ) {

            console.log("partner_id")

            const lot = await loadLot(barcode)

            console.log({lot})

            if(lot && lot?.product_id && lot?.product_id?.length != 0) {

                this.trigger('flash');
                
                const producto = await loadProduct(lot.product_id[0])

                console.log({producto})
                
                const rec = await loadRecord(lot.id);

                console.log({rec})

                const actualizar = await updateRecord(rec.id);

                console.log({actualizar})

                const fieldsParams = {
                    // "id": rec.id,
                    "lot_id" : {
                        "id" : lot.id,
                        "name" : lot.display_name,
                    },
                    "lot_name" : lot.display_name,
                    "product_id": {
                        "id": producto.id,
                        "barcode": producto.barcode,
                        "categ_id": producto.categ_id[0],
                        "code": producto.code,
                        "default_code": producto.default_code,
                        "display_name": producto.display_name,
                        "has_image": producto.has_image || false,
                        "is_storable": producto.is_storable || true,
                        "tracking": producto.tracking || "none",
                        "uom_id": producto.uom_id[0],
                        "use_time": producto.use_time || 0
                    },
                    "qty_done": actualizar.qty
                };

                console.log({fieldsParams});

                let encuentra = false;

                for(const line of this.pageLines){
                    // console.log(line, lot);
                    if(line?.lot_id?.id == lot?.id){
                        encuentra = true;
                    }
                }
                console.log({encuentra})
                if(!encuentra){   
                    currentLine = await this.createNewLine({ fieldsParams });
                }
                else{
                    window.alert("Esta caja ya fue escaneada");
                }

                console.log({currentLine})
                console.log({"lineas": this.pageLines})
                
            }
            return false;

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
        
        if (barcodeData.package) {
            // Object.assign(barcodeData, this._retrievePackageData(barcodeData));

            console.log("asignando el paquete")
            
            console.log(this.pageLines)
            // Assign the result_package_id to all lines that are not complete
            for (const line of this.pageLines) {
                console.log(line)
                if (!line.result_package_id) {
                    await this.updateLine(line, { result_package_id: barcodeData.package.id });
                }
            }

            // Reload the content without reloading the page
            // console.log(this.load, this.reloadingMoveLines)
            
            if(this.load)
                await this.load();
            // if(this.reloadingMoveLines)
            //     await this.reloadingMoveLines();
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

        console.log("fieldsParams from barcode", this._convertDataToFieldsParams(barcodeData))
        console.log("currentLine", currentLine)

        if (currentLine) {
            console.log("Ya hay linea")
            if(currentLine?.lot_id?.id != barcodeData?.lot?.id){
                const qty = await getPackage(barcodeData?.product?.id) || 1
                currentLine = await this.createNewLine({fieldsParams: {...this._convertDataToFieldsParams(barcodeData), qty_done: qty}});
                if (currentLine) {
                    this.trigger("playSound", "success");
                }
            }
            else{
                
                const qty = await getPackage(barcodeData?.product?.id) || 1
                await this.updateLine(currentLine, {fieldsParams: {...this._convertDataToFieldsParams(barcodeData), qty_done: qty}});
                this.trigger("playSound", "success");
            }
        } else {
            console.log("No hay linea")
            const qty = await getPackage(barcodeData?.product?.id) || 1
            currentLine = await this.createNewLine({fieldsParams: {...this._convertDataToFieldsParams(barcodeData), qty_done: qty}});
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
        //console.log("barcode", barcode);
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
        //console.log({barcode});
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
