import { Checkout } from '@website_sale/interactions/checkout';
import { patch } from '@web/core/utils/patch';
patch(Checkout.prototype, {
    async toggleBillingAddressRow(ev) {
        const useDeliveryAsBilling = ev.target.checked;
        const addDeliveryAddressButton = this.el.querySelector(
            '.o_address_card_add_new[data-address-type="delivery"]'
        );
        if (addDeliveryAddressButton) {
            const addDeliveryUrl = new URL(addDeliveryAddressButton.href);
            addDeliveryUrl.searchParams.set(
                'use_delivery_as_billing', encodeURIComponent(useDeliveryAsBilling)
            );
            addDeliveryAddressButton.href = addDeliveryUrl.toString();
        }
        if (useDeliveryAsBilling) {
            this.billingContainer.classList.add('d-none');
            const selectedDeliveryAddress = this._getSelectedAddress('delivery');
            if (selectedDeliveryAddress) {
                await this.waitFor(
                    this._selectMatchingBillingAddress(selectedDeliveryAddress.dataset.partnerId)
                );
            }
        } else {
            this._disableMainButton();
            this.billingContainer.classList.remove('d-none');
        }
        this.addBillingAddressBtn?.classList.toggle('d-none', useDeliveryAsBilling);
        this._enableMainButton();
    },
});
