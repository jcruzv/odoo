/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";

console.log("custom KPIs loaded")

class CustomKPIs extends Component {
    static template = "custom_kpis.Template";
    setup() {
        const hoy = new Date();

        const auxSaved = localStorage.getItem("savedKPIs") || "{}";
        const savedKPIs = JSON.parse(auxSaved);
        const savedDate = savedKPIs?.date || hoy.toISOString().split("T")[0]; // Obtener la fecha guardada o la fecha actual si no existe
        const savedCliente = savedKPIs?.cliente || "Todos"; // Obtener el cliente guardado o "Todos" si no existe
        const savedPeriodo = savedKPIs?.periodo || "Día"; // Obtener el periodo guardado o "Día" si no existe

        this.state = useState({
            cliente: savedCliente,
            periodo: savedPeriodo,
            creadasAyer: [],
            creadasHoy: [],
            registrosAyer: [],
            registrosHoy: [],
            surtidasAyer: [],
            surtidasHoy: [],
            retrasoAyer: [],
            retrasoHoy: [],
            surtidasRetraso: [],
            pendientesRetraso: [],
            otifHoy: [],
            clasePendientes: 'kpi-item',
            claseRetraso: 'kpi-item',
            date: savedDate
        });

        // Save the date whenever it changes
        this.state.date = savedDate;
        this.onDateChange({ target: { value: savedDate } })
    }

    // Método para actualizar el valor del KPI

    async onClienteChange(event) {
        const cliente = event.target.value;
        this.state.cliente = cliente;
        const auxSaved = localStorage.getItem("savedKPIs") || "{}";
        const savedKPIs = JSON.parse(auxSaved);
        savedKPIs.cliente = cliente; // Actualizar el cliente guardado
        localStorage.setItem("savedKPIs", JSON.stringify(savedKPIs)); // Guardar el cliente en localStorage
        this.getData()
    }
    
    async onPeriodoChange(event) {
        const periodo = event.target.value;
        this.state.periodo = periodo;
        if(periodo == "Día"){
            this.state.date = new Date().toISOString().split("T")[0]
        }
        else if(periodo == "Semana"){
            const hoy = new Date();
            this.state.date = Math.ceil((hoy - new Date(hoy.getFullYear(), 0, 1)) / (1000 * 60 * 60 * 24 * 7));
        }
        else if(periodo == "Mes"){
            const hoy = new Date();
            this.state.date = hoy.getMonth() + 1;
        }
        this.onDateChange({ target: { value: this.state.date } })
        
        const auxSaved = localStorage.getItem("savedKPIs") || "{}";
        const savedKPIs = JSON.parse(auxSaved);
        savedKPIs.periodo = periodo; // Actualizar el periodo guardado
        localStorage.setItem("savedKPIs", JSON.stringify(savedKPIs)); // Guardar el periodo en localStorage
    }

    async onDateChange(event) {
        const formatoOdoo = (fecha) => {
            // 2025-03-21 00:19:35
            const year = fecha.getFullYear().toString().padStart(4, '0');
            const month = (fecha.getMonth() + 1).toString().padStart(2, '0'); // Meses de 0 a 11
            const day = fecha.getDate().toString().padStart(2, '0');
            const hour = fecha.getHours().toString().padStart(2, '0');
            const minute = fecha.getMinutes().toString().padStart(2, '0');
            const second = fecha.getSeconds().toString().padStart(2, '0');
            return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
        }

        let dateStartUTC = ""
        let dateEndUTC = ""
        let dateStartUTC2 = ""
        let dateEndUTC2 = ""
        
        if(this.state.periodo == "Día"){
            const newDate = event.target.value;
            dateStartUTC = new Date(new Date(newDate)); // Parse as UTC
            dateStartUTC.setHours(dateStartUTC.getHours() + 12); // Restar 5 horas para GMT-5
            dateEndUTC = new Date(newDate); // Parse as UTC
            dateEndUTC.setHours(dateEndUTC.getHours() + 36); // Restar 5 horas para GMT-5
            
            // dia anterior
            dateStartUTC2 = new Date(newDate); // Parse as UTC
            dateStartUTC2.setDate(dateStartUTC2.getDate() - 1); // Restar un día
            dateStartUTC2.setHours(dateStartUTC2.getHours() + 12); // Restar 5 horas para GMT-5
            dateEndUTC2 = new Date(newDate); // Parse as UTC
            dateEndUTC2.setDate(dateEndUTC2.getDate() - 1); // Restar un día
            dateEndUTC2.setHours(dateEndUTC2.getHours() + 36); // Restar 5 horas para GMT-5
    
            this.state.date = newDate;
        }
        else if(this.state.periodo == "Semana"){
            const week = event.target.value; //numero de la semana del año
            const year = new Date().getFullYear(); // año actual
            const firstDayOfYear = new Date(year, 0, 1);
            const adjustFirstDay = (firstDayOfYear.getDay() <= 4) ? 1 - firstDayOfYear.getDay() : 8 - firstDayOfYear.getDay(); // ajustar el primer día de la semana
            firstDayOfYear.setDate(firstDayOfYear.getDate() + adjustFirstDay); // ajustar el primer día de la semana
            const daysToAdd = (week - 1) * 7; // calcular los días a añadir
            
            const mondayOfWeek = new Date(firstDayOfYear.getTime() + daysToAdd * 24 * 60 * 60 * 1000);
            const sundayOfWeek = new Date(mondayOfWeek.getTime() + 6 * 24 * 60 * 60 * 1000);

            dateStartUTC = new Date(mondayOfWeek); // Parse as UTC
            dateStartUTC.setHours(dateStartUTC.getHours() + 12); // Restar 5 horas para GMT-5
            dateEndUTC = new Date(sundayOfWeek); // Parse as UTC
            dateEndUTC.setHours(dateEndUTC.getHours() + 36); // Restar 5 horas para GMT-5
            
            // restar una semana y asignar dateStartUTC2 y dateEndUTC2
            dateStartUTC2 = new Date(mondayOfWeek); // Parse as UTC
            dateStartUTC2.setDate(dateStartUTC2.getDate() - 7); // Restar un día
            dateStartUTC2.setHours(dateStartUTC2.getHours() + 12); // Restar 5 horas para GMT-5
            dateEndUTC2 = new Date(sundayOfWeek); // Parse as UTC
            dateEndUTC2.setDate(dateEndUTC2.getDate() - 7); // Restar un día
            dateEndUTC2.setHours(dateEndUTC2.getHours() + 36); // Restar 5 horas para GMT-5


            const dateEnd = new Date(sundayOfWeek); // Parse as UTC
            // dateEnd.setHours(dateEndUTC.getHours() + 36); // Restar 5 horas para GMT-5
            console.log(dateEnd)
            this.state.dateEnd = formatoOdoo(dateEnd);

            this.state.date = week;
        }
        else if(this.state.periodo == "Mes"){
            const month = event.target.value; //numero del mes del año
            const year = new Date().getFullYear(); // año actual
            const firstDayOfMonth = new Date(year, month - 1, 1); // primer día del mes
            const lastDayOfMonth = new Date(year, month, 0); // último día del mes

            // pasar a utc y asignar a datestartUTC y dateEndUTC
            dateStartUTC = new Date(firstDayOfMonth); // Parse as UTC
            dateStartUTC.setHours(dateStartUTC.getHours() + 12); // Restar 5 horas para GMT-5
            dateEndUTC = new Date(lastDayOfMonth); // Parse as UTC
            dateEndUTC.setHours(dateEndUTC.getHours() + 36); // Restar 5 horas para GMT-5

            // restar un mes y asignar dateStartUTC2 y dateEndUTC2
            dateStartUTC2 = new Date(firstDayOfMonth); // Parse as UTC
            dateStartUTC2.setMonth(dateStartUTC2.getMonth() - 1); // Restar un mes
            dateStartUTC2.setHours(dateStartUTC2.getHours() + 12); // Restar 5 horas para GMT-5
            dateEndUTC2 = new Date(lastDayOfMonth); // Parse as UTC
            dateEndUTC2.setMonth(dateEndUTC2.getMonth() - 1); // Restar un mes
            dateEndUTC2.setHours(dateEndUTC2.getHours() + 36); // Restar 5 horas para GMT-5
            this.state.date = month;
        }

        this.state.dateStartUTC = formatoOdoo(dateStartUTC);
        this.state.dateEndUTC = formatoOdoo(dateEndUTC);
        this.state.dateStartUTC2 = formatoOdoo(dateStartUTC2);
        this.state.dateEndUTC2 = formatoOdoo(dateEndUTC2);

        
        const auxSaved = localStorage.getItem("savedKPIs") || "{}";
        const savedKPIs = JSON.parse(auxSaved);
        savedKPIs.date = event.target.value; // Actualizar la fecha guardada
        localStorage.setItem("savedKPIs", JSON.stringify(savedKPIs)); // Guardar la fecha en localStorage

        this.getData()
    }

    async onSiguiente(event){
        if(this.state.periodo == "Día"){
            const newDate = new Date(this.state.date);
            newDate.setDate(newDate.getDate() + 1);
            this.onDateChange({ target: { value: newDate.toISOString().split("T")[0] } })
        }
        else if(this.state.periodo == "Semana"){
            const week = parseInt(this.state.date) + 1;
            this.onDateChange({ target: { value: week } })
        }
        else if(this.state.periodo == "Mes"){
            const month = parseInt(this.state.date) + 1;
            this.onDateChange({ target: { value: month } })
        }
    }
    async onAnterior(event){
        if(this.state.periodo == "Día"){
            const newDate = new Date(this.state.date);
            newDate.setDate(newDate.getDate() - 1);
            this.onDateChange({ target: { value: newDate.toISOString().split("T")[0] } })
        }
        else if(this.state.periodo == "Semana"){
            const week = parseInt(this.state.date) - 1;
            this.onDateChange({ target: { value: week } })
        }
        else if(this.state.periodo == "Mes"){
            const month = parseInt(this.state.date) - 1;
            this.onDateChange({ target: { value: month } })
        }
    }

    async getData(){
        
        const company_ids = this.env.services.company.activeCompanyIds;

        const filters = [
            ["date", ">=", this.state.dateStartUTC],
            ["date", "<=", this.state.dateEndUTC],
            ["state", "in", ["assigned", "done"]],
            ["picking_type_id", "in", [90, 203]],
            ["company_id", "in", company_ids],
        ];

        if (this.state.cliente !== "Todos") {
            filters.push(["partner_id", "=", this.state.cliente*1]);
        }
        
        const creadasHoy = await this.env.services.orm.searchRead("stock.picking", filters, []);

        console.log({creadasHoy})

        const registrosHoyFilters = [
            ["scheduled_date", ">=", this.state.dateStartUTC],
            ["scheduled_date", "<=", this.state.dateEndUTC],
            ["state", "in", ["assigned", "done"]],
            ["picking_type_id", "in", [90, 203]],
            ["company_id", "in", company_ids],
        ];
        if (this.state.cliente !== "Todos") {
            registrosHoyFilters.push(["partner_id", "=", this.state.cliente*1]);
        }
        const registrosHoy = await this.env.services.orm.searchRead("stock.picking", registrosHoyFilters, []);

        const retrasoHoy = registrosHoy.filter((registro) => registro.onTime == 'Atrasado' || registro.onTime == 'delayed');

        const retrasoAyerFilters = [
            ["scheduled_date", "<=", this.state.dateEndUTC2],
            ["state", "in", ["assigned", "waiting"]],
            ["picking_type_id", "in", [90, 203]],
            ["company_id", "in", company_ids],
        ];
        if (this.state.cliente !== "Todos") {
            retrasoAyerFilters.push(["partner_id", "=", this.state.cliente*1]);
        }
        const retrasoAyer = await this.env.services.orm.searchRead("stock.picking", retrasoAyerFilters, []);

        const otifHoy = registrosHoy.filter((registro) => registro.onTime == 'En tiempo' || registro.onTime == 'on_time');

        const creadasAyerFilters = [
            ["date", ">=", this.state.dateStartUTC2],
            ["date", "<=", this.state.dateEndUTC2],
            ["state", "in", ["assigned", "done"]],
            ["picking_type_id", "in", [90, 203]],
            ["company_id", "in", company_ids],
        ];
        if (this.state.cliente !== "Todos") {
            creadasAyerFilters.push(["partner_id", "=", this.state.cliente*1]);
        }
        const creadasAyer = await this.env.services.orm.searchRead("stock.picking", creadasAyerFilters, []);

        const registrosAyerFilters = [
            ["scheduled_date", ">=", this.state.dateStartUTC2],
            ["scheduled_date", "<=", this.state.dateEndUTC2],
            ["state", "in", ["assigned", "done"]],
            ["picking_type_id", "in", [90, 203]],
            ["company_id", "in", company_ids],
        ];
        if (this.state.cliente !== "Todos") {
            registrosAyerFilters.push(["partner_id", "=", this.state.cliente*1]);
        }
        const registrosAyer = await this.env.services.orm.searchRead("stock.picking", registrosAyerFilters, []);

        const surtidasAyer = registrosAyer.filter((registro) => registro.state === "done");
        const surtidasHoy = registrosHoy.filter((registro) => registro.state === "done");
        
        const filtrosAuxSurtidasRetraso = [
            ["scheduled_date", "<=", this.state.dateEndUTC],
            ["date_done", ">=", this.state.dateStartUTC],
            ["date_done", "<=", this.state.dateEndUTC],
            ["state", "in", ["done"]],
            ["picking_type_id", "in", [90, 203]],
            ["company_id", "in", company_ids],
        ]
        
        if (this.state.cliente !== "Todos") {
            filtrosAuxSurtidasRetraso.push(["partner_id", "=", this.state.cliente*1]);
        }

        const auxSurtidasRetraso = await this.env.services.orm.searchRead("stock.picking", filtrosAuxSurtidasRetraso, []);

        const surtidasRetraso = [...auxSurtidasRetraso, ...registrosHoy, ...retrasoAyer].filter((registro) => registro.state == 'done' && (registro.onTime == 'Atrasado' || registro.onTime == 'delayed'))
        const pendientesRetraso = [registrosHoy, ...retrasoAyer].filter((registro) => registro.state == 'assigned' && (registro.onTime == 'Atrasado' || registro.onTime == 'delayed'))
        const registrosPendientes = [registrosHoy, ...retrasoAyer].filter((registro) => registro.state == 'assigned' && (registro.onTime == 'Pendiente' || registro.onTime == 'pending'))
        // this.state.registrosPendientes = registrosPendientes || [];

        this.state.registrosHoy = [...registrosHoy, ...retrasoAyer] || [];
        this.state.registrosAyer = registrosAyer || [];
        this.state.retrasoHoy = retrasoHoy || [];
        this.state.otifHoy = otifHoy || [];
        if(registrosAyer.length > 0){
            this.state.otif = Math.round(otifHoy.length/(this.state.registrosHoy.length) * 10000)/100 || 0;
        }
        else{
            this.state.otif = 0;
        }
        this.state.surtidasAyer = surtidasAyer || [];
        this.state.surtidasHoy = surtidasHoy || [];
        this.state.creadasHoy = creadasHoy || [];
        this.state.creadasAyer = creadasAyer || [];
        this.state.retrasoHoy = retrasoHoy || [];
        this.state.retrasoAyer = retrasoAyer || [];
        this.state.surtidasHoy = surtidasHoy || [];
        this.state.surtidasAyer = surtidasAyer || [];
        this.state.surtidasRetraso = surtidasRetraso || [];
        this.state.pendientesRetraso = pendientesRetraso || [];

        this.state.clasePendientes = registrosPendientes.length > 10 ? 'kpi-item text-warning' : 'kpi-item';
        this.state.clasePendientes = registrosPendientes.length > 20 ? 'kpi-item text-danger' : this.state.clasePendientes;

        this.state.claseRetraso = retrasoHoy.length > 0 ? 'kpi-item text-warning' : 'kpi-item';
        this.state.claseRetraso = retrasoHoy.length > 5 ? 'kpi-item text-danger' : this.state.claseRetraso;

    }

    onClickCreadasAyer() {
        if (this.state.creadasAyer && this.state.creadasAyer.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Creadas Ayer",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.creadasAyer.map(r => r.id)]],
            });
        } else {
            console.warn("No creadasAyer available for action.");
        }
    }

    onClickRecibidasAyer() {
        if (this.state.registrosAyer && this.state.registrosAyer.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Recibidas Ayer",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.registrosAyer.map(r => r.id)]],
            });
        } else {
            console.warn("No registrosAyer available for action.");
        }
    }

    onClickSurtidasAyer() {
        if (this.state.surtidasAyer && this.state.surtidasAyer.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Surtidas Ayer",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.surtidasAyer.map(r => r.id)]],
            });
        } else {
            console.warn("No surtidasAyer available for action.");
        }
    }

    onClickRetrasoAyer() {
        if (this.state.retrasoAyer && this.state.retrasoAyer.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Retraso Ayer",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.retrasoAyer.map(r => r.id)]],
            });
        } else {
            console.warn("No retrasoAyer available for action.");
        }
    }

    onClickCreadasHoy() {
        if (this.state.creadasHoy && this.state.creadasHoy.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Creadas Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.creadasHoy.map(r => r.id)]],
            });
        } else {
            console.warn("No creadasHoy available for action.");
        }
    }

    onClickRecibidasHoy() {
        if (this.state.registrosHoy && this.state.registrosHoy.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Recibidas Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.registrosHoy.map(r => r.id)]],
            });
        } else {
            console.warn("No registrosHoy available for action.");
        }
    }

    onClickSurtidasHoy() {
        if (this.state.surtidasHoy && this.state.surtidasHoy.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Surtidas Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.surtidasHoy.map(r => r.id)]],
            });
        } else {
            console.warn("No surtidasHoy available for action.");
        }
    }

    onClickRetrasoHoy() {
        if (this.state.retrasoHoy && this.state.retrasoHoy.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Retraso Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.retrasoHoy.map(r => r.id)]],
            });
        } else {
            console.warn("No retrasoHoy available for action.");
        }
    }

    onClickSurtidasRetrasoHoy() {
        if (this.state.surtidasRetraso && this.state.surtidasRetraso.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Surtidas con Retraso Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.surtidasRetraso.map(r => r.id)]],
            });
        } else {
            console.warn("No surtidasRetraso available for action.");
        }
    }

    onClickPendientesRetrasoHoy() {
        if (this.state.pendientesRetraso && this.state.pendientesRetraso.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Pendientes con Retraso Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.pendientesRetraso.map(r => r.id)]],
            });
        } else {
            console.warn("No pendientesRetraso available for action.");
        }
    }
    onClickOTIFHoy() {
        if (this.state.otifHoy && this.state.otifHoy.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "OTIF Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.otifHoy.map(r => r.id)]],
            });
        } else {
            console.warn("No otifHoy available for action.");
        }
    }
}

// REGISTRAR EL COMPONENTE EN LA CATEGORÍA "actions"
registry.category("actions").add("custom_kpis", CustomKPIs);
