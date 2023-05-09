odoo.define('lod_kokkokm.models', function (require) {
"use strict";

    var models = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var core = require('web.core');
    var _t = core._t;

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        init_from_JSON: function(json){
            _super_order.init_from_JSON.apply(this,arguments);
            this.order_validate = json.order_validate || false
        },

        export_as_JSON: function () {
            let json = _super_order.export_as_JSON.apply(this, arguments);
            json['order_validate'] = this.order_validate
            return json;
        },

        export_for_printing: function(){
            var json = _super_order.export_for_printing.apply(this, arguments);
            var to_return = _.extend(json, {
                    order_validate: this.order_validate,
                });
            return to_return;
        },
    });

});