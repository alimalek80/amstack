/**
 * JavaScript for handling price field visibility in Post admin
 */
(function($) {
    'use strict';
    
    function togglePriceField() {
        var isFreeCheckbox = $('#id_is_free');
        var priceField = $('.field-price');
        
        if (isFreeCheckbox.is(':checked')) {
            priceField.hide();
            $('#id_price').val('0.00');
        } else {
            priceField.show();
            // Set a default price if empty
            if (!$('#id_price').val() || $('#id_price').val() === '0.00') {
                $('#id_price').val('1.00');
            }
        }
    }
    
    function handlePriceChange() {
        var priceInput = $('#id_price');
        var isFreeCheckbox = $('#id_is_free');
        var priceValue = parseFloat(priceInput.val()) || 0;
        
        if (priceValue > 0) {
            isFreeCheckbox.prop('checked', false);
        } else {
            isFreeCheckbox.prop('checked', true);
        }
    }
    
    $(document).ready(function() {
        // Add helpful text
        $('.field-price .help').remove();
        $('.field-price').append('<div class="help">Enter the price in USD. Set to 0.00 for free content.</div>');
        
        // Initial state
        togglePriceField();
        
        // Handle is_free checkbox changes
        $('#id_is_free').change(function() {
            togglePriceField();
        });
        
        // Handle price input changes
        $('#id_price').on('input change', function() {
            handlePriceChange();
        });
        
        // Add visual indicators
        $('.field-is_free label').append(' <span style="color: #666; font-size: 0.9em;">(Check for free content)</span>');
        $('.field-price label').append(' <span style="color: #666; font-size: 0.9em;">(USD)</span>');
    });
    
})(django.jQuery);