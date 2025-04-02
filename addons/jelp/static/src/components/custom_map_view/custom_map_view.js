/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component, useState } from "@odoo/owl";

console.log("custom map loaded")

class CustomMapView extends Component {
    static template = "custom_map_view.Template";
    setup() {
        // pasar los valores a la vista
        console.log(this)
        const { track_state, partner_latitude, partner_longitude, track_longitude, track_latitude } = this.props.action.context;
        console.log(track_state, partner_latitude, partner_longitude, track_longitude, track_latitude)
        const url = `https://www.google.com/maps/dir/${partner_latitude},${partner_longitude}/${track_latitude},${track_longitude}/`;
        console.log(url)
        console.log({
            trackState: track_state,
            trackLongitude: track_longitude,
            trackLatitude: track_latitude,
            url: url,
        })
        this.state = useState({
            trackState: track_state,
            trackLongitude: track_longitude,
            trackLatitude: track_latitude,
            url: url,
        });
    }
}

// REGISTRAR EL COMPONENTE EN LA CATEGORÍA "actions"
registry.category("actions").add("custom_map_view", CustomMapView);
