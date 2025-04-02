/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";

class TrackStateView extends Component {
    static template = "TrackStateView"; // Ensure this matches the template ID in XML

    setup() {
        this.trackState = this.props.default_track_state || "N/A";
        this.trackLongitude = this.props.default_track_longitude || "N/A";
        this.trackLatitude = this.props.default_track_latitude || "N/A";
    }
}

// Register the component in the actions registry
registry.category("actions").add("track_state_owl_view", TrackStateView);

export default TrackStateView;
