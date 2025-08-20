/**
 * Fiat to Crypto Conversion
 * Handles the client-side conversion of fiat amounts to crypto amounts
 * and updates the UI accordingly.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const form = document.querySelector('form');
    const fiatAmountInput = document.getElementById('fiat_amount');
    const fiatCurrencySelect = document.getElementById('fiat_currency');
    const cryptoAmountInput = document.getElementById('crypto_amount');
    const cryptoCurrencyInput = document.getElementById('crypto_currency');
    const exchangeRateInput = document.getElementById('exchange_rate');
    const rateExpiryInput = document.getElementById('rate_expiry');
    
    // Check if we're on a page with the conversion form
    if (!form || !fiatAmountInput || !fiatCurrencySelect) {
        return;
    }
    
    // State
    let rateExpiryTimer = null;
    
    // Initialize the form
    initForm();
    
    // Event listeners
    fiatAmountInput.addEventListener('input', handleAmountChange);
    fiatCurrencySelect.addEventListener('change', handleCurrencyChange);
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    /**
     * Initialize the form
     */
    function initForm() {
        // If we have an amount and currency, fetch the rate
        if (fiatAmountInput.value && fiatCurrencySelect.value) {
            updateCryptoAmount();
        }
        
        // Check if we have an existing rate that's still valid
        checkExistingRate();
    }
    
    /**
     * Handle changes to the amount input
     */
    function handleAmountChange() {
        updateCryptoAmount();
    }
    
    /**
     * Handle changes to the currency select
     */
    function handleCurrencyChange() {
        updateCryptoAmount();
    }
    
    /**
     * Check if we have an existing rate that's still valid
     */
    function checkExistingRate() {
        if (!exchangeRateInput.value || !rateExpiryInput.value) {
            return false;
        }
        
        const expiry = new Date(rateExpiryInput.value);
        const now = new Date();
        
        if (expiry > now) {
            // Rate is still valid, set up expiry timer
            const timeUntilExpiry = expiry - now;
            setupRateExpiryTimer(timeUntilExpiry);
            return true;
        }
        
        // Rate has expired, clear the inputs
        exchangeRateInput.value = '';
        rateExpiryInput.value = '';
        return false;
    }
    
    /**
     * Update the crypto amount based on the current fiat amount and currency
     */
    async function updateCryptoAmount() {
        const amount = parseFloat(fiatAmountInput.value);
        const currency = fiatCurrencySelect.value;
        
        if (!amount || amount <= 0 || !currency) {
            resetCryptoAmount();
            return;
        }
        
        try {
            // Show loading state
            cryptoAmountInput.value = 'Calculating...';
            
            // Get the exchange rate and calculate the crypto amount
            const response = await fetch(`/api/exchange/convert?amount=${amount}&fiat_currency=${currency}&crypto_currency=BTC`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Failed to get exchange rate');
            }
            
            // Update the form fields
            cryptoAmountInput.value = `${parseFloat(data.crypto_amount).toFixed(8)} ${data.crypto_currency}`;
            cryptoCurrencyInput.value = data.crypto_currency;
            exchangeRateInput.value = data.exchange_rate;
            rateExpiryInput.value = data.rate_expiry;
            
            // Set up the rate expiry timer
            const expiry = new Date(data.rate_expiry);
            const now = new Date();
            const timeUntilExpiry = expiry - now;
            
            setupRateExpiryTimer(timeUntilExpiry);
            
            // Show success message
            showAlert('Exchange rate updated successfully', 'success');
            
        } catch (error) {
            console.error('Error updating crypto amount:', error);
            showAlert(`Error: ${error.message}`, 'danger');
            resetCryptoAmount();
        }
    }
    
    /**
     * Reset the crypto amount and related fields
     */
    function resetCryptoAmount() {
        cryptoAmountInput.value = '';
        cryptoCurrencyInput.value = '';
        exchangeRateInput.value = '';
        rateExpiryInput.value = '';
        
        if (rateExpiryTimer) {
            clearTimeout(rateExpiryTimer);
            rateExpiryTimer = null;
        }
    }
    
    /**
     * Set up a timer to handle rate expiry
     * @param {number} timeUntilExpiry - Time in milliseconds until the rate expires
     */
    function setupRateExpiryTimer(timeUntilExpiry) {
        if (timeUntilExpiry <= 0) {
            handleRateExpired();
            return;
        }
        
        // Clear any existing timer
        if (rateExpiryTimer) {
            clearTimeout(rateExpiryTimer);
        }
        
        // Set up a new timer
        rateExpiryTimer = setTimeout(() => {
            handleRateExpired();
        }, timeUntilExpiry);
        
        // Update the UI to show when the rate will expire
        const minutes = Math.ceil(timeUntilExpiry / (60 * 1000));
        const expiryElement = document.getElementById('rate-expiry-notice');
        if (expiryElement) {
            expiryElement.textContent = `Rate expires in ${minutes} minute${minutes !== 1 ? 's' : ''}`;
            expiryElement.classList.remove('d-none');
        }
    }
    
    /**
     * Handle the rate expiry
     */
    function handleRateExpired() {
        showAlert('The exchange rate has expired. Please update the amount to get a new rate.', 'warning');
        
        // Update the UI
        const expiryElement = document.getElementById('rate-expiry-notice');
        if (expiryElement) {
            expiryElement.textContent = 'Rate expired';
            expiryElement.classList.add('text-danger');
        }
        
        // Disable the form submission
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
        }
    }
    
    /**
     * Show an alert message
     * @param {string} message - The message to display
     * @param {string} type - The alert type (e.g., 'success', 'danger', 'warning')
     */
    function showAlert(message, type = 'info') {
        // Remove any existing alerts
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        // Create the alert element
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert the alert before the form
        form.parentNode.insertBefore(alert, form);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    }
});
