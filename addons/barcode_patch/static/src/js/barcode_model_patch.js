/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import BarcodeModel from '@stock_barcode/models/barcode_model';
import { _t } from "@web/core/l10n/translation";
import { BarcodeObject } from "@stock_barcode/barcode_object";

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
            
            const products = records.map(x=>x.product_id[0])
            
            const lotes = await this.orm.searchRead("stock.lot", [["display_name", "=", lote], ["product_id", "in", products]], ["id", "product_id", "display_name"]);
            
            if (lotes.length > 0) {
                return lotes[0];
            }
        }

        const loadProduct = async (product) => {

            const records = await this.orm.searchRead("product.product", [["id", "=", product]], ["id", "barcode", "categ_id", "code", "default_code", "display_name", "has_image", "is_storable", "tracking", "uom_id", "use_time"]);
            
            if (records.length > 0) {
                return records[0];
            }
        }

        const loadRecord = async (lot_id) => {

            const records = await this.orm.searchRead("stock.move", [["picking_id", "=", this.resId]], ["id"]);

            const moves = records.map(x=>x.id)
            
            const records2 = await this.orm.searchRead("stock.move.line", [["move_id", "in", moves], ["lot_id", "=", lot_id]], ["id"]);

            if (records2.length > 0) {
                return records2[0];
            }
        }

        const updateRecord = async (id) => {

            const producto = await this.orm.searchRead("stock.move.line", [["id", "=", id]], ["id", "product_id"]);

            const embalaje = await this.orm.searchRead("product.packaging", [["product_id", "=", producto[0].product_id[0]]], ["qty"]);
                        
            await this.orm.write("stock.move.line", [id], { quantity: embalaje[0].qty });

            return embalaje[0];
            // Opcional: Volver a cargar el registro para reflejar los cambios
            // await this.loadRecord();
        }
        
        const getPackage = async (id) => {
            
            if(!id)
                return false;
            
            const embalaje = await this.orm.searchRead("product.packaging", [["product_id", "=", id]], ["qty"]);

            if(embalaje.length!=0)
                return embalaje[0]?.qty || 1;
            else
                return false;
            // Opcional: Volver a cargar el registro para reflejar los cambios
            // await this.loadRecord();
        }
        let barcodeData = {};
        let currentLine = false;
        // Creates a filter if needed, which can help to get the right record
        // when multiple records have the same model and barcode.
        const filters = {};
        if (this.selectedLine && this.selectedLine.product_id.tracking !== 'none') {
            filters['stock.lot'] = {
                product_id: this.selectedLine.product_id.id,
            };
        }
        // Constrain DB reads to records which belong to the company defined on the open operation
        filters['all'] = {
            company_id: [false].concat(this._getCompanyId() || []),
        };
        try {
            barcodeData = await this._parseBarcode(barcode, filters);
            if (this._shouldSearchForAnotherLot(barcodeData, filters)) {
                // Retry to parse the barcode without filters in case it matches an existing
                // record that can't be found because of the filters
                const lot = await this.cache.getRecordByBarcode(barcode, 'stock.lot');
                if (lot) {
                    Object.assign(barcodeData, { lot, match: true });
                }
            }
        } catch (parseErrorMessage) {
            barcodeData.error = parseErrorMessage;
        }

        // Keep in memory every scans.
        this.scanHistory.unshift(barcodeData);



        const cliente = this.cache.dbIdCache["stock.picking"][this.resId].partner_id;

        // Si el cliente es MINISO
        if (cliente == 260 &&
            (
                barcodeData.error || 
                (barcodeData.lotName && barcodeData.lotName !== null) ||
                (barcodeData.lot && barcodeData.lot !== null)
            )
        ) {

            const lot = await loadLot(barcode)

            if(lot && lot?.product_id && lot?.product_id?.length != 0) {

                this.trigger('flash');
                
                const producto = await loadProduct(lot.product_id[0])

                const rec = await loadRecord(lot.id);

                const actualizar = await updateRecord(rec.id);

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

                let encuentra = false;

                for(const line of this.pageLines){
                    if(line?.lot_id?.id == lot?.id){
                        encuentra = true;
                    }
                }
                
                if(!encuentra){   
                    currentLine = await this.createNewLine({ fieldsParams });
                }
                else{
                    window.alert("Esta caja ya fue escaneada");
                }               
            }
            return false;

        }
        // es procesa
        else if(cliente == 275){
            // si el sku(barcode) no se encuentra en el stock.picking de recibo, alertar.
            const picking = await this.orm.searchRead("stock.picking", [["id", "=", this.resId]], ["id", "product_id", "display_name", "picking_type_id"]);
            const code = await this.orm.searchRead("stock.picking.type", [["id", "=", picking[0].picking_type_id[0]]], ["id", "code"]);
            console.log({picking})
            if(code[0].code == "incoming"){
                if(picking.length == 0){
                    window.alert("El producto no se encuentra en el recibo.");
                    return false;
                }
                const records = await this.orm.searchRead("stock.move", [["picking_id", "=", this.resId]], ["id", "product_id", "display_name"]);
                if(records.length == 0){
                    window.alert("El producto no se encuentra en el recibo.");
                    return false;
                }
            }
        }

        if (barcodeData.match) { // Makes flash the screen if the scanned barcode was recognized.
            this.trigger('flash');
        }

        // Process each data in order, starting with non-ambiguous data type.
        if (barcodeData.action) { // As action is always a single data, call it and do nothing else.
            return await barcodeData.action();
        }

        if (barcodeData.packaging) {
            Object.assign(barcodeData, this._retrievePackagingData(barcodeData));
        }

        if (barcodeData.package) {

            // Assign the result_package_id to all lines that are not complete
            for (const line of this.pageLines) {
                if (!line.result_package_id) {
                    await this.updateLine(line, { result_package_id: barcodeData.package.id });
                }
            }

        }

        // Depending of the configuration, the user can be forced to scan a specific barcode type.
        const check = this._checkBarcode(barcodeData);
        if (check.error) {
            return this.notification(check.message, { title: check.title, type: "danger" });
        }

        if (barcodeData.product) { // Remembers the product if a (packaging) product was scanned.
            this.lastScanned.product = barcodeData.product;
        }

        if (barcodeData.lot && !barcodeData.product) {
            Object.assign(barcodeData, this._retrieveTrackingNumberInfo(barcodeData.lot));
        }

        await this._processLocation(barcodeData);
        await this._processPackage(barcodeData);
        if (barcodeData.stopped) {
            // TODO: Sometime we want to stop here instead of keeping doing thing,
            // but it's a little hacky, it could be better to don't have to do that.
            return;
        }

        if (barcodeData.weight) { // Convert the weight into quantity.
            barcodeData.quantity = barcodeData.weight.value;
        }

        // If no product found, take the one from last scanned line if possible.
        if (!barcodeData.product) {
            if (barcodeData.quantity) {
                currentLine = this.selectedLine || this.lastScannedLine;
            } else if (this.selectedLine && this.selectedLine.product_id.tracking !== 'none') {
                currentLine = this.selectedLine;
            } else if (this.lastScannedLine && this.lastScannedLine.product_id.tracking !== 'none') {
                currentLine = this.lastScannedLine;
            }
            if (currentLine) { // If we can, get the product from the previous line.
                const previousProduct = currentLine.product_id;
                // If the current product is tracked and the barcode doesn't fit
                // anything else, we assume it's a new lot/serial number.
                if (previousProduct.tracking !== 'none' &&
                    !barcodeData.match && this.canCreateNewLot) {
                    this.trigger('flash');
                    barcodeData.lotName = barcode;
                    barcodeData.product = previousProduct;
                }
                if (barcodeData.lot || barcodeData.lotName ||
                    barcodeData.quantity) {
                    barcodeData.product = previousProduct;
                }
            }
        }
        let { product } = barcodeData;
        if (!product && barcodeData.match && this.parser.nomenclature.is_gs1_nomenclature) {
            // Special case where something was found using the GS1 nomenclature but no product is
            // used (eg.: a product's barcode can be read as a lot is starting with 21).
            // In such case, tries to find a record with the barcode by by-passing the parser.
            barcodeData = await this._fetchRecordFromTheCache(barcode, filters);
            if (barcodeData.packaging) {
                Object.assign(barcodeData, this._retrievePackagingData(barcodeData));
            } else if (barcodeData.lot) {
                Object.assign(barcodeData, this._retrieveTrackingNumberInfo(barcodeData.lot));
            }
            if (barcodeData.product) {
                product = barcodeData.product;
            } else if (barcodeData.match) {
                await this._processPackage(barcodeData);
                if (barcodeData.stopped) {
                    return;
                }
            }
        }
        if (!product) { // Product is mandatory, if no product, raises a warning.
            return this.noProductToast(barcodeData);
        } else if (barcodeData.lot && barcodeData.lot.product_id !== product.id) {
            delete barcodeData.lot; // The product was scanned alongside another product's lot.
        }
        if (barcodeData.weight) { // the encoded weight is based on the product's UoM
            barcodeData.uom = this.cache.getRecord('uom.uom', product.uom_id);
        }

        // Searches and selects a line if needed.
        if (!currentLine || this._shouldSearchForAnotherLine(currentLine, barcodeData)) {
            currentLine = this._findLine(barcodeData);
        }

        // Default quantity set to 1 by default if the product is untracked or
        // if there is a scanned tracking number.
        if (product.tracking === 'none' || barcodeData.lot || barcodeData.lotName || this._incrementTrackedLine()) {
            const hasUnassignedQty = currentLine && currentLine.qty_done && !currentLine.lot_id && !currentLine.lot_name;
            const isTrackingNumber = barcodeData.lot || barcodeData.lotName;
            const defaultQuantity = isTrackingNumber && hasUnassignedQty ? 0 : 1;
            barcodeData.quantity = barcodeData.quantity || defaultQuantity;
            if (product.tracking === 'serial' && barcodeData.quantity > 1 && (barcodeData.lot || barcodeData.lotName)) {
                barcodeData.quantity = 1;
                this.notification(
                    _t(`A product tracked by serial numbers can't have multiple quantities for the same serial number.`),
                    { type: 'danger' }
                );
            }
        }

        if ((barcodeData.lotName || barcodeData.lot) && product) {
            const lotName = barcodeData.lotName || barcodeData.lot.name;
            for (const line of this.currentState.lines) {
                if (line.product_id.id !== product.id) {
                    continue; // The same SN can be scanned for different product.
                }
                if (line.product_id.tracking === "serial" && this.getQtyDone(line) !== 0 &&
                    this.getlotName(line) === lotName) {
                    return this.notification(
                        _t("The scanned serial number %s is already used.", lotName),
                        { type: 'danger' }
                    );
                }
            }
            // Prefills `owner_id` and `package_id` if possible.
            const prefilledOwner = (!currentLine || (currentLine && !currentLine.owner_id)) && this.groups.group_tracking_owner && !barcodeData.owner;
            const prefilledPackage = (!currentLine || (currentLine && !currentLine.package_id)) && this.groups.group_tracking_lot && !barcodeData.package;
            if (this.useExistingLots && (prefilledOwner || prefilledPackage)) {
                const lotId = (barcodeData.lot && barcodeData.lot.id) || (currentLine && currentLine.lot_id && currentLine.lot_id.id) || false;
                const locationId = (currentLine && currentLine.location_id && currentLine.location_id.id) || false;
                const params = {
                    lot_id: lotId,
                    lot_name: (!lotId && barcodeData.lotName) || false,
                };
                let quants = await this.cache.getQuants(product, locationId, params);
                if (quants.length && quants.length > 1 && (prefilledPackage || prefilledOwner)) {
                    // If we have multiple matching quants and we use package and/or consigment,
                    // give priority to the quants with a package or an owner.
                    const filteredQuants = quants.filter((quant) => {
                        return quant.package_id || quant.owner_id;
                    });
                    quants = filteredQuants.length ? filteredQuants : quants;
                }
                if (quants && quants.length === 1) {
                    const quant = quants[0];
                    if (prefilledPackage && quant.package_id) {
                        barcodeData.package = this.cache.getRecord("stock.quant.package", quant.package_id);
                    }
                    if (prefilledOwner && quant.owner_id) {
                        barcodeData.owner = this.cache.getRecord("res.partner", quant.owner_id);
                    }
                }
            }
        }

        // Updates or creates a line based on barcode data.
        if (currentLine) { // If line found, can it be incremented ?
            console.log("Ya hay linea")
            const categoria = currentLine.product_id.categ_id;
            
            if(categoria == 20){ //Es miniso
                if(currentLine?.lot_id?.id != barcodeData?.lot?.id){
                    const qty = await getPackage(barcodeData?.product?.id) || 1
                    
                    currentLine = await this.createNewLine({fieldsParams: {...this._convertDataToFieldsParams(barcodeData), qty_done: qty}});
                    if (currentLine) {
                        this.trigger("playSound", "success");
                    }
                }
                else{
                    window.alert("Esta caja ya fue escaneada");
                    const qty = await getPackage(barcodeData?.product?.id)
                    if(qty){
                        await this.updateLine(currentLine, {fieldsParams: {...this._convertDataToFieldsParams(barcodeData), qty_done: qty}});
                        this.trigger("playSound", "success");
                    }
                }
            }
            else{
                if (this.selectedLine && this.selectedLine.product_id.barcode === barcode) {
                    console.log("Actualizar", this.selectedLine);
                    const currentQty = this.selectedLine.qty_done || 0; // Ensure qty_done is initialized
                    const updatedQty = currentQty + 1;
                    console.log({ currentQty, updatedQty });
                    await this.updateLine(this.selectedLine, { qty_done: 1 });
                    this.trigger("playSound", "success");
                    await this.save();
                    return false;
                }
                else{

                    let exceedingQuantity = 0;
                    if (product.tracking !== 'serial' && barcodeData.uom && barcodeData.uom.category_id == currentLine.product_uom_id.category_id) {
                        // convert to current line's uom
                        barcodeData.quantity = (barcodeData.quantity / barcodeData.uom.factor) * currentLine.product_uom_id.factor;
                        barcodeData.uom = currentLine.product_uom_id;
                    }
                    // Checks the quantity doesn't exceed the line's remaining quantity.
                    if (currentLine.reserved_uom_qty && product.tracking === 'none') {
                        const remainingQty = currentLine.reserved_uom_qty - currentLine.qty_done;
                        if (barcodeData.quantity > remainingQty && this._shouldCreateLineOnExceed(currentLine)) {
                            // In this case, lowers the increment quantity and keeps
                            // the excess quantity to create a new line.
                            exceedingQuantity = barcodeData.quantity - remainingQty;
                            barcodeData.quantity = remainingQty;
                        }
                    }
                    if (barcodeData.quantity > 0 || barcodeData.lot || barcodeData.lotName) {
                        const fieldsParams = this._convertDataToFieldsParams(barcodeData);
                        if (barcodeData.uom) {
                            fieldsParams.uom = barcodeData.uom;
                        }
                        await this.updateLine(currentLine, fieldsParams);
                        this.trigger("playSound", "success");
                    }
                    if (exceedingQuantity) { // Creates a new line for the excess quantity.
                        barcodeData.quantity = exceedingQuantity;
                        const fieldsParams = this._convertDataToFieldsParams(barcodeData);
                        if (barcodeData.uom) {
                            fieldsParams.uom = barcodeData.uom;
                        }
                        currentLine = await this._createNewLine({
                            copyOf: currentLine,
                            fieldsParams,
                        });
                    }
                }
            }
        } else { // No line found, so creates a new one.
            console.log("No hay linea")
            const fieldsParams = this._convertDataToFieldsParams(barcodeData);
            console.log(fieldsParams)
            const categoria = fieldsParams.product_id.categ_id;
            
            const picking = await this.orm.searchRead("stock.picking", [["id", "=", this.resId]], ["id", "product_id", "display_name", "picking_type_id"]);
            const code = await this.orm.searchRead("stock.picking.type", [["id", "=", picking[0].picking_type_id[0]]], ["id", "code"]);
            console.log({picking})
            if(code[0].code == "incoming"){
                if(categoria == 24){ //Es factor pesca
                    window.alert("Este producto no está registrado en el Recibo")
                    return false;
                }
            }
            if (barcodeData.uom) {
                fieldsParams.uom = barcodeData.uom;
            }

            if(categoria == 20){
                const qty = await getPackage(fieldsParams?.product_id?.id)
                if(qty){
                    await this.createNewLine({fieldsParams:{...fieldsParams, qty_done: qty}});
                    this.trigger("playSound", "success");
                }
            }
            else{
                if (this.createSingleLinesForPackaging(barcodeData)) {
                    for (let lineCount = 0; lineCount < barcodeData.packaging.qty; lineCount++) {
                        currentLine = await this.createNewLine({fieldsParams});
                    }
                } else {
                    currentLine = await this.createNewLine({fieldsParams});
                }
            }
            if(currentLine){
                this.trigger("playSound", "success");
            }
        }

        // And finally, if the scanned barcode modified a line, selects this line.
        if (currentLine) {
            this._selectLine(currentLine);
        }

        const matchedURI = barcode.match(/^urn:.*$/);
        if (matchedURI) {
            // If the process goes right and the scanned barcode is an URI, add
            // it to the cache to avoid scanning it a second time.
            this.uriCache.add(barcode);
        }
        this.trigger('update');
        console.log("va a guardar")
        await this.save();

        for (const line of this.currentState.lines) {
            if (!line.id) {
            const savedLine = await this.orm.searchRead(this.lineModel, [["virtual_id", "=", line.virtual_id]], ["id"]);
            if (savedLine.length > 0) {
                line.id = savedLine[0].id;
            }
            }
        }
        
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
    },
    
    async deleteLine(line) {
        console.log("Delete Line")
        console.log(line)
        if(line.product_id.categ_id == 20 || line.product_id.categ_id == 24){ //Es miniso o factor pesca
            const index = this.currentState.lines.findIndex(l => l.virtual_id === line.virtual_id);

            if (line.parent_id) { // Check if the line is a subline
                this.currentState.lines[index].qty_done = 0;
                this.linesToSave = this.linesToSave.filter(vId => vId !== line.virtual_id);
                if (line.id) {
                    await this.orm.write(this.lineModel, [line.id], { quantity: 0 });
                    this.trigger('refresh');
                }
            } else {
                this.currentState.lines.splice(index, 1);
                line.qty_done = 0;
                this.linesToSave = this.linesToSave.filter(vId => vId !== line.virtual_id);
                if (line.id) {
                    await this.orm.write(this.lineModel, [line.id], { quantity: 0 });
                    this.trigger('refresh');
                }
            }
            // window.alert("No puedes eliminar este producto.")
            // return false;
            
        }
        else{

            if (!line.id) {
                // The line doesn't exist in the DB yet => Delete it only in the frontend.
                const index = this.currentState.lines.findIndex(l => l.virtual_id === line.virtual_id);
                this.currentState.lines.splice(index, 1);
                this.linesToSave = this.linesToSave.filter(vId => vId !== line.virtual_id);
            } else {
                await this.save();
                await this.orm.call(this.lineModel, this.deleteLineMethod, [line.id]);
                this.trigger('refresh');
            }
        }
    }
    
    
});
