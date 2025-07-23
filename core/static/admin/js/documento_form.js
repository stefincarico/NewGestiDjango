// in core/static/admin/js/documento_form.js
window.addEventListener('load', function() {
    (function($) {
        const tipoDocSelect = $('#id_tipo_documento');
        
        // Selezioniamo le "righe" dei campi che vogliamo manipolare
        const clienteRow = $('.form-row.field-cliente');
        const fornitoreRow = $('.form-row.field-fornitore');
        const cantiereRow = $('.form-row.field-cantiere');
        const numeroDocRow = $('.form-row.field-numero_documento'); // <-- Selezioniamo la riga del numero

        function toggleFieldsBasedOnDocType() {
            const tipoDoc = tipoDocSelect.val();

            if (tipoDoc.includes('Vendita')) {
                // Logica per documenti di VENDITA
                clienteRow.show();
                cantiereRow.show();
                fornitoreRow.hide();
                numeroDocRow.hide(); // Nascondi numero_documento (è automatico)
            } else if (tipoDoc.includes('Acquisto')) {
                // Logica per documenti di ACQUISTO
                clienteRow.hide();
                cantiereRow.hide();
                fornitoreRow.show();
                numeroDocRow.show(); // Mostra numero_documento (è manuale e obbligatorio)
            } else {
                // Stato iniziale o tipo non selezionato
                clienteRow.hide();
                cantiereRow.hide();
                fornitoreRow.hide();
                numeroDocRow.hide();
            }
        }

        // Esegui la funzione al caricamento della pagina e ogni volta che il tipo cambia
        toggleFieldsBasedOnDocType();
        tipoDocSelect.on('change', toggleFieldsBasedOnDocType);

    })(django.jQuery);
});