// in core/static/admin/js/documento_form.js
window.addEventListener('load', function() {
    (function($) {
        const tipoDocSelect = $('#id_tipo_documento');
        const contentTypeRow = $('.form-row.field-content_type');
        const objectIdRow = $('.form-row.field-object_id');
        const contentTypeSelect = contentTypeRow.find('select');

        function updateContactFields() {
            const tipoDoc = tipoDocSelect.val();
            let targetModelName = null;

            if (tipoDoc && tipoDoc.includes('Vendita')) {
                targetModelName = 'cliente';
            } else if (tipoDoc && tipoDoc.includes('Acquisto')) {
                targetModelName = 'fornitore';
            }

            if (targetModelName) {
                const option = contentTypeSelect.find('option').filter(function() {
                    return $(this).text().toLowerCase().includes(targetModelName);
                });
                
                if (option.length) {
                    contentTypeSelect.val(option.val());
                    contentTypeRow.hide();
                    objectIdRow.show();
                }
            } else {
                // Se non c'è un tipo documento o non è né vendita né acquisto
                contentTypeRow.show();
                objectIdRow.hide();
                // Resetta il valore per evitare selezioni residue
                contentTypeSelect.val('');
            }
        }

        tipoDocSelect.on('change', updateContactFields);
        updateContactFields(); // Esegui al caricamento

    })(django.jQuery);
});