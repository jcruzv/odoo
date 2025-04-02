/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";

console.log("custom KPIs loaded")

class CustomKPIs extends Component {
    static template = "custom_kpis.Template";
    setup() {
        const hoy = new Date();

        console.log(this)
        this.state = useState({
            registrosHoy: [],
            registrosAyer: [],
            retrasoHoy: [],
            registrosPendientes: [],
            otifHoy: [],
            surtidasAyer: [],
            clasePendientes: 'kpi-item',
            claseRetraso: 'kpi-item',
            date : hoy.toISOString().split("T")[0]
        });
        this.onDateChange({ target: { value: hoy.toISOString().split("T")[0] } })
    }

    // Método para actualizar el valor del KPI
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

        const newDate = event.target.value;

        const dateStartUTC = new Date(new Date(newDate)); // Parse as UTC
        dateStartUTC.setHours(dateStartUTC.getHours() + 12); // Restar 5 horas para GMT-5
        const dateEndUTC = new Date(newDate); // Parse as UTC
        dateEndUTC.setHours(dateEndUTC.getHours() + 36); // Restar 5 horas para GMT-5

        const registrosHoy = await this.env.services.orm.searchRead("stock.picking", [
            ["scheduled_date", ">=", formatoOdoo(dateStartUTC)],
            ["scheduled_date", "<=", formatoOdoo(dateEndUTC)],
        ], []);

        // dia anterior
        const dateStartUTC2 = new Date(newDate); // Parse as UTC
        dateStartUTC2.setDate(dateStartUTC2.getDate() - 1); // Restar un día
        dateStartUTC2.setHours(dateStartUTC2.getHours() + 12); // Restar 5 horas para GMT-5
        const dateEndUTC2 = new Date(newDate); // Parse as UTC
        dateEndUTC2.setDate(dateEndUTC2.getDate() - 1); // Restar un día
        dateEndUTC2.setHours(dateEndUTC2.getHours() + 36); // Restar 5 horas para GMT-5

        console.log(formatoOdoo(dateStartUTC), formatoOdoo(dateEndUTC))
        console.log(formatoOdoo(dateStartUTC2), formatoOdoo(dateEndUTC2))

        const retrasoHoy = registrosHoy.filter((registro) => registro.onTime == 'Atrasado' || registro.onTime == 'delayed');
        const otifHoy = registrosHoy.filter((registro) => registro.onTime == 'En tiempo' || registro.onTime == 'on_time');

        
        const registrosAyer = await this.env.services.orm.searchRead("stock.picking", [
            ["scheduled_date", ">=", formatoOdoo(dateStartUTC2)],
            ["scheduled_date", "<=", formatoOdoo(dateEndUTC2)],
        ], []);

        const surtidasAyer = registrosAyer.filter((registro) => registro.state === "done");


        console.log("Registros de hoy:", registrosHoy)

        console.log("Registros de ayer:", registrosAyer)

        const registrosPendientes = registrosAyer.filter((registro) => registro.state === "assigned" || registro.state === "waiting");

        this.state.registrosHoy = registrosHoy || [];
        this.state.registrosAyer = registrosAyer || [];
        this.state.registrosPendientes = registrosPendientes || [];
        this.state.retrasoHoy = retrasoHoy || [];
        this.state.otifHoy = otifHoy || [];
        if(registrosPendientes.length + registrosAyer.length > 0){
            this.state.otif = otifHoy.length/(registrosPendientes.length + registrosAyer.length) * 100 || 0;
        }
        else{
            this.state.otif = 0;
        }
        this.state.surtidasAyer = surtidasAyer || [];

        this.state.clasePendientes = registrosPendientes.length > 10 ? 'kpi-item text-warning' : 'kpi-item';
        this.state.clasePendientes = registrosPendientes.length > 20 ? 'kpi-item text-danger' : this.state.clasePendientes;

        this.state.claseRetraso = retrasoHoy.length > 0 ? 'kpi-item text-warning' : 'kpi-item';
        this.state.claseRetraso = retrasoHoy.length > 5 ? 'kpi-item text-danger' : this.state.claseRetraso;

        this.state.date = newDate;
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

    onClickPendientes() {
        if (this.state.registrosPendientes && this.state.registrosPendientes.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "Pendientes Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                views: [[false, 'list'], [false, 'form']],
                domain: [["id", "in", this.state.registrosPendientes.map(r => r.id)]],
            });
        } else {
            console.warn("No registrosPendientes available for action.");
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

    onClickOTIFHoy() {
        if (this.state.otifHoy && this.state.otifHoy.length > 0) {
            this.env.services.action.doAction({
                type: "ir.actions.act_window",
                name: "OTIF Hoy",
                res_model: "stock.picking",
                view_mode: "list",
                domain: [["id", "in", this.state.otifHoy.map(r => r.id)]],
            });
        } else {
            console.warn("No otifHoy available for action.");
        }
    }
}

// REGISTRAR EL COMPONENTE EN LA CATEGORÍA "actions"
registry.category("actions").add("custom_kpis", CustomKPIs);
