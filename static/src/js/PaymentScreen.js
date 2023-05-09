odoo.define('lod_kokkokm.PaymentScreen', function (require) {
"use strict";

    require('bus.BusService')
    const Chrome = require('point_of_sale.Chrome');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
	const Registries = require('point_of_sale.Registries');
//    var bus = require('lod_kokkokm.bus');
    var bus = require('custom_reward_cr.bus');

    const lodKOKPaymentScreen = (PaymentScreen) => class extends PaymentScreen {
        constructor() {
            super(...arguments);
            this.bus = bus.bus;
            this.bus.on("notification", this, this.on_notification);
            this.bus.start_polling();
        }

        async on_notification(notifications) {
            var self = this;
            var order = self.env.pos.get_order()
            const line = self.paymentLines.find((line) => line.payment_method.is_kok_payment)

            var payment_amount = 0
            var kkp_amount = 0
            var payment_ref = ''
            var phone = ''

            var next_screen = false

            if (line){
                for (var i=0; i<notifications.length; i++) {
                    if (notifications[i][1].payload.type && !order.order_validate || order.order_validate == undefined &&
                        notifications[i][0] == undefined && notifications[i][1].type == "pos.validate" && notifications[i][1].payload.type.phone != undefined){
                        var order_name = notifications[i][1].payload.type.order_name
                        console.log("\n +++++++ call back phone +++++++", notifications[i][1].payload.type.phone)
                        if (order.name == order_name && line != undefined && !order.order_validate){
                            phone = notifications[i][1].payload.type.phone
                            // payment_amount = notifications[i][1].payload.type.amount
                            kkp_amount = notifications[i][1].payload.type.amount
                            payment_ref = notifications[i][1].payload.type.payment_ref
                            order.order_validate = true

                            var client =  self.currentOrder.get_client()
                            var lines = order.get_orderlines();
                            var category_ids = ''
                            if (client){
                                _.each(this.env.pos.cash_back_config, function (cash_back) {
                                    if (client.membership_level == cash_back.membership_level){
                                        console.log("\n +++++++ exc_product_categ_ids +++++++", cash_back.exc_product_categ_ids)
                                        category_ids = cash_back.exc_product_categ_ids
                                    }
                                });
                            }
                            console.log("\n +++++++ category_ids +++++++", category_ids)
                            lines.map(function(line){
                                if (category_ids.indexOf(line.product.categ_id[0]) == -1){
                                    payment_amount += line.get_display_price()
                                    // console.log("\n +++++++ get_display_price +++++++", line.get_display_price())
                                    // console.log("\n +++++++ quantity +++++++", line.quantity)
                                }	           
                            });

                            var cash_amount = 0;
                            var cash_config = false
                            
                            if (payment_amount <= kkp_amount && client){
                                _.each(this.env.pos.cash_back_config, function (cash_back) {
                                    if (cash_back.from_amount <= payment_amount &&
                                        payment_amount <= cash_back.to_amount && client.membership_level == cash_back.membership_level){
                                        cash_amount = (cash_back.percentage * payment_amount) / 100
                                        cash_config = cash_back.id
                                    }
                                });
                            }
                            else {
                                if (kkp_amount > 0){
                                    _.each(this.env.pos.cash_back_config, function (cash_back) {
                                        if (cash_back.from_amount <= kkp_amount &&
                                            kkp_amount <= cash_back.to_amount && client.membership_level == cash_back.membership_level){
                                            cash_amount = (cash_back.percentage * kkp_amount) / 100
                                            cash_config = cash_back.id
                                        }
                                    });
                                }
                            }
                            // console.log("\n +++++++ Float payment_amount +++++++", cash_amount.toFixed(2))
                            order.kok_payment_ref = payment_ref
                            order.phone_kkp = phone
                            order.cashback_amount = cash_amount.toFixed(2)
                          
                            if (cash_amount > 0 && cash_config){                                
                                self.rpc({
                                    model: 'cash.back.config',
                                    method: 'post_cash_in',
                                    args: [
                                        [], order.name, cash_amount, client.id, payment_ref, phone
                                    ],
                                });
                                // console.log("\n ++++++++ validateOrder +++++++")
                            }
                            self.validateOrder(true);
                            next_screen = true                            
                        }
                    }
                }
            }
            if (order.order_validate){
                // console.log("\n ++++++++ NextScreen +++++++", self.nextScreen)
                self.showScreen(self.nextScreen);
            }
        }
    };

    Registries.Component.extend(PaymentScreen, lodKOKPaymentScreen);
    return lodKOKPaymentScreen;
});