{
    'name': 'Customize KokkoM',
    'version': '15',
    'sequence': 0,
    'category': 'All',
    'website': 'https://www.laoodoo.com',
    'summary': '',
    'description': """Customize for KokkoM""",
    'depends': ['base', 'product', 'purchase', 'point_of_sale', 'website_sale', 'mrp', 'base_address_city', 'contacts',
                'bi_internal_wallet', 'stock', 'account_accountant', 'pos_kok_payment_cr', 'custom_reward_cr'],
    'data': [
        'security/ir.model.access.csv',

        'data/product_data.xml',

        'wizard/update_categories_view.xml',
        'wizard/unpack_view.xml',
        'wizard/product_batch_price_wizard_view.xml',
        'wizard/product_calculate_sale_price_wizard_view.xml',

        'views/product_view.xml',
        'views/product_template_views.xml',
        'views/pos_config_view.xml',
        'views/ib_trans_no_view.xml',
        'views/purchase_order_view.xml',
        'views/account.xml',
        'views/res_partner_view.xml',
        'views/stock_views.xml',
        'views/product_batch_price_views.xml',
        

        'views/frontend/check_price.xml',
        'views/frontend/page.xml',
        'views/inventory_views.xml',
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'assets': {
        'point_of_sale.assets': [
            'lod_kokkokm/static/src/js/models.js',
            'lod_kokkokm//static/src/js/bus.js',
            'lod_kokkokm/static/src/js/PaymentScreen.js',
        ],
        'web.assets_backend': [
            '/lod_kokkokm/static/src/scss/kokkok.scss',
        ],
        'web.assets_frontend': [
            '/lod_kokkokm/static/src/scss/check_price.scss',
        ],
    },
    'license': 'LGPL-3',
}
