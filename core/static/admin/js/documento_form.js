// in core/static/admin/js/documento_form.js
window.addEventListener('load', function() {
    (function($) {
        const tipoDocSelect = $('#id_tipo_documento');
        
        // Trova le "righe" dei campi nel form dell'admin
        const clienteRow = $('.form-row.field-cliente');
        const fornitoreRow = $('.form-row.field-fornitore');
        const cantiereRow = $('.form-row.field-cantiere');

        function toggleContactFields() {
            const tipoDoc = tipoDocSelect.val();

            if (tipoDoc.includes('Vendita')) {
                clienteRow.show();
                cantiereRow.show();
                fornitoreRow.hide();
            } else if (tipoDoc.includes('Acquisto')) {
                clienteRow.hide();
                cantiereRow.hide();
                fornitoreRow.show();
            } else {
                // Se non è selezionato nulla, nascondi tutto
                clienteRow.hide();
                cantiereRow.hide();
                fornitoreRow.hide();
            }
        }

        // Esegui la funzione al caricamento e ogni volta che il tipo cambia
        toggleContactFields();
        tipoDocSelect.on('change', toggleContactFields);

    })(django.jQuery);
});