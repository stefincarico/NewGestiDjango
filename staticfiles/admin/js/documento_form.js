// in core/static/admin/js/documento_form.js

window.addEventListener('load', function() {
    (function($) {
        const tipoDocSelect = $('#id_tipo_documento');
        const contentTypeSelect = $('#id_content_type');
        const objectIdRow = $('.form-row.field-object_id');

        function updateContactType() {
            const tipoDoc = tipoDocSelect.val();
            let targetModel = null;

            if (tipoDoc.includes('Vendita')) {
                targetModel = 'cliente';
            } else if (tipoDoc.includes('Acquisto')) {
                targetModel = 'fornitore';
            }

            if (targetModel) {
                // Trova l'option che contiene il nome del modello target
                const optionToSelect = contentTypeSelect.find('option:contains(' + targetModel + ')');
                if (optionToSelect.length > 0) {
                    contentTypeSelect.val(optionToSelect.val());
                    // Nascondi il selettore del content type perché la scelta è automatica
                    $('.form-row.field-content_type').hide();
                    objectIdRow.show();
                }
            } else {
                 // Se non è né vendita né acquisto, mostra tutto
                 $('.form-row.field-content_type').show();
                 objectIdRow.hide();
            }
        }

        // Lega la funzione all'evento change e eseguila subito
        tipoDocSelect.on('change', updateContactType);
        updateContactType();

    })(django.jQuery);
});