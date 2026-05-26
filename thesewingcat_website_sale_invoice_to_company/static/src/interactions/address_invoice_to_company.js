import { CustomerAddress } from '@portal/interactions/address';
import { patch } from '@web/core/utils/patch';

patch(CustomerAddress.prototype, {
    setup() {
        super.setup();
        this.invoiceToCompanyInput = this.addressForm?.invoice_to_company;
        this.invoiceFields = ['company_name', 'vat'];
        if (this.invoiceToCompanyInput) {
            this._boundOnChangeInvoiceToCompany = this._syncInvoiceRequirements.bind(this);
            this.invoiceToCompanyInput.addEventListener('change', this._boundOnChangeInvoiceToCompany);
            this._syncInvoiceRequirements();
        }
    },

    async _onChangeCountry(init = false) {
        await super._onChangeCountry(init);
        this._syncInvoiceRequirements();
    },

    destroy() {
        if (this.invoiceToCompanyInput && this._boundOnChangeInvoiceToCompany) {
            this.invoiceToCompanyInput.removeEventListener('change', this._boundOnChangeInvoiceToCompany);
        }
        super.destroy();
    },

    _syncInvoiceRequirements() {
        if (!this.addressForm || !this.invoiceToCompanyInput) {
            return;
        }
        const required = this.invoiceToCompanyInput.checked;
        for (const fieldName of this.invoiceFields) {
            const input = this.addressForm[fieldName];
            if (!input) {
                continue;
            }
            this._markRequired(fieldName, required);
            if (!required) {
                input.classList.remove('is-invalid');
            }
        }
        if (!required && !this.addressForm.querySelector('.is-invalid')) {
            this.errorsDiv?.replaceChildren();
        }
    },
});

