from django.contrib import admin
from .models import (
    AliquotaIVA, ModalitaPagamento,
    Cliente, Fornitore, Dipendente,
    Cantiere, DocumentoTestata, DocumentoRiga , Scadenza
)


@admin.register(AliquotaIVA)
class AliquotaIVAAdmin(admin.ModelAdmin):
    list_display = (
        'descrizione', 'valore_percentuale', 'attivo', 
        'created_at', 'updated_at', 'created_by', 'updated_by'
    )
    list_filter = ('attivo',)
    search_fields = ('descrizione',)
    
    # Usa exclude per nascondere i campi dal form
    exclude = ('created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        # La nostra logica di salvataggio automatico rimane identica
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ModalitaPagamento)
class ModalitaPagamentoAdmin(admin.ModelAdmin):
    # Mostra tutte le informazioni utili nella lista
    list_display = (
        'descrizione', 
        'giorni_scadenza', 
        'attivo', 
        'created_at', 
        'updated_at', 
        'created_by', 
        'updated_by'
    )
    
    # Aggiunge i filtri e la ricerca per una migliore navigazione
    list_filter = ('attivo',)
    search_fields = ('descrizione',)

    # Esclude i campi di audit dal form per una UI pulita
    exclude = ('created_by', 'updated_by')
    
    # Mantiene la logica di salvataggio automatico
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_cognome_ragione_sociale', 'partita_iva', 'codice_fiscale', 'citta', 'attivo')
    search_fields = ('nome_cognome_ragione_sociale', 'partita_iva', 'codice_fiscale')
    list_filter = ('attivo', 'citta')
    exclude = ('created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Fornitore)
class FornitoreAdmin(admin.ModelAdmin):
    list_display = ('nome_cognome_ragione_sociale', 'partita_iva', 'codice_fiscale', 'citta', 'attivo')
    search_fields = ('nome_cognome_ragione_sociale', 'partita_iva', 'codice_fiscale')
    list_filter = ('attivo', 'citta')
    exclude = ('created_by', 'updated_by')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Dipendente)
class DipendenteAdmin(admin.ModelAdmin):
    list_display = ('nome_cognome_ragione_sociale', 'mansione', 'data_assunzione', 'attivo')
    search_fields = ('nome_cognome_ragione_sociale', 'mansione')
    list_filter = ('attivo', 'mansione')
    exclude = ('created_by', 'updated_by')
    
    # Con fieldsets possiamo raggruppare i campi nel form
    fieldsets = (
        ('Dati Anagrafici', {
            'fields': (
                'nome_cognome_ragione_sociale', 
                ('codice_fiscale', 'partita_iva'),
                'attivo'
            )
        }),
        ('Dati di Contatto', {
            'fields': ('indirizzo', 'cap', 'citta', 'provincia', 'email', 'telefono')
        }),
        ('Dati Lavorativi', {
            'fields': ('mansione', 'data_assunzione', 'data_fine_rapporto', 'costo_orario', 'note_generali')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Cantiere)
class CantiereAdmin(admin.ModelAdmin):
    list_display = ('codice_cantiere', 'descrizione', 'cliente', 'stato', 'data_inizio')
    search_fields = ('codice_cantiere', 'descrizione', 'cliente__nome_cognome_ragione_sociale')
    list_filter = ('stato', 'cliente')
    exclude = ('created_by', 'updated_by')
    
    fieldsets = (
        ('Informazioni Principali', {
            'fields': (
                ('codice_cantiere', 'stato'),
                'descrizione',
                'cliente'
            )
        }),
        ('Dettagli Logistici', {
            'fields': ('indirizzo',)
        }),
        ('Date', {
            'fields': ('data_inizio', 'data_fine_prevista', 'data_chiusura_effettiva')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

# --- Classi per Documenti (Versione Finale) ---

class DocumentoRigaInline(admin.TabularInline):
    model = DocumentoRiga
    readonly_fields = ('imponibile_riga', 'iva_riga')
    extra = 1

@admin.register(DocumentoTestata)
class DocumentoTestataAdmin(admin.ModelAdmin):
    # --- 1. CONFIGURAZIONE DELLA LISTA ---
    # Aggiungiamo 'data_documento' e la rendiamo ordinabile di default.
    # Specifichiamo che solo 'numero_documento' è il link al dettaglio.
    list_display = ('numero_documento', 'data_documento', 'contatto', 'stato', 'totale')
    list_display_links = ('numero_documento',)
    list_filter = ('stato', 'tipo_documento', 'data_documento')
    search_fields = ('numero_documento', 'cliente__nome_cognome_ragione_sociale', 'fornitore__nome_cognome_ragione_sociale')
    raw_id_fields = ('cliente', 'fornitore', 'cantiere')
    readonly_fields = ('imponibile', 'iva', 'totale', 'created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = [DocumentoRigaInline]

    # --- 2. GESTIONE DINAMICA DEL FORM ---
    # Questa classe dice a Django di caricare il nostro JavaScript.
    class Media:
        js = ('admin/js/documento_form.js',)
        
    # Questo metodo nasconde il campo 'numero_documento' SOLO quando creiamo un nuovo oggetto.
    def get_fieldsets(self, request, obj=None):
        base_fields = (
            ('tipo_documento', 'stato'),
            'data_documento',
            'cliente',
            'fornitore',
            'cantiere',
            'modalita_pagamento'
        )
        # Se stiamo modificando un oggetto esistente, mostriamo anche il suo numero
        if obj:
            base_fields = ('numero_documento',) + base_fields
            
        return (
            ('Informazioni Principali', {'fields': base_fields}),
            ('Riepilogo', {'classes': ('collapse',), 'fields': self.readonly_fields}),
            ('Note', {'fields': ('note',)})
        )
    
    def get_readonly_fields(self, request, obj=None):
        # Se stiamo modificando un oggetto (obj esiste)...
        if obj:
            # ...restituisci la lista originale PIÙ 'numero_documento'
            return self.readonly_fields + ('numero_documento',)
        # Altrimenti (in creazione), restituisci solo la lista originale
        return self.readonly_fields

    # --- 3. LOGICA DI SALVATAGGIO E NUMERAZIONE ---
    def save_model(self, request, obj, form, change):
        # La logica di audit viene eseguita sempre
        obj.updated_by = request.user
        
        # La logica di creazione/numerazione viene eseguita solo per i nuovi oggetti
        if not obj.pk:
            obj.created_by = request.user
            
            from django.utils import timezone
            current_year = timezone.now().year
            
            doc_type = obj.tipo_documento
            prefix = ""
            
            # Determina il prefisso in base al tipo di documento
            if doc_type == DocumentoTestata.TipoDocumento.FATTURA_VENDITA:
                prefix = f"FT-{current_year}-"
            elif doc_type == DocumentoTestata.TipoDocumento.NOTA_CREDITO_VENDITA:
                prefix = f"NC-{current_year}-"

            # Se è un tipo di documento che richiede numerazione automatica...
            if prefix:
                # Trova l'ultimo documento dello stesso tipo e dello stesso anno
                last_doc = DocumentoTestata.objects.filter(
                    tipo_documento=doc_type,
                    data_documento__year=current_year
                ).order_by('numero_documento').last()
                
                new_number = 1
                if last_doc and last_doc.numero_documento.startswith(prefix):
                    try:
                        last_number_str = last_doc.numero_documento.replace(prefix, '')
                        new_number = int(last_number_str) + 1
                    except (ValueError, IndexError):
                        new_number = 1
                
                obj.numero_documento = f"{prefix}{new_number:06d}"
        
        # Infine, chiama il metodo di salvataggio originale
        super().save_model(request, obj, form, change)

    # --- METODI HELPER (invariati ma necessari) ---
    @admin.display(description='Contatto')
    def contatto(self, obj):
        if obj.cliente:
            return obj.cliente
        if obj.fornitore:
            return obj.fornitore
        return "-"
        
    def save_formset(self, request, form, formset, change):
        formset.save()
        testata = form.instance
        testata.imponibile = sum(r.imponibile_riga for r in testata.righe.all() if r.imponibile_riga is not None)
        testata.iva = sum(r.iva_riga for r in testata.righe.all() if r.iva_riga is not None)
        testata.totale = testata.imponibile + testata.iva
        testata.save()
        super().save_formset(request, form, formset, change)



@admin.register(Scadenza)
class ScadenzaAdmin(admin.ModelAdmin):
    list_display = (
        'data_scadenza', 
        'anagrafica', 
        'importo', 
        'importo_residuo',
        'stato', 
        'documento',
        'is_scaduta'
    )
    list_filter = ('stato', 'tipo_scadenza', 'data_scadenza')
    search_fields = ('documento__numero_documento', 'anagrafica__nome_cognome_ragione_sociale')
    list_display_links = ('data_scadenza', 'anagrafica')
    
    # Rendiamo i campi calcolati e relazionati non modificabili direttamente
    readonly_fields = ('importo_residuo', 'is_scaduta', 'created_at', 'updated_at', 'created_by', 'updated_by')