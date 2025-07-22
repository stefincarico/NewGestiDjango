from django.contrib import admin
from .models import (
    AliquotaIVA, ModalitaPagamento,
    Cliente, Fornitore, Dipendente,
    Cantiere, DocumentoTestata, DocumentoRiga 
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
    # --- MODIFICA QUI: Mostriamo un campo 'contatto' personalizzato ---
    list_display = ('__str__', 'contatto', 'stato', 'totale')
    list_filter = ('stato', 'tipo_documento', 'data_documento')
    search_fields = ('numero_documento', 'cliente__nome_cognome_ragione_sociale', 'fornitore__nome_cognome_ragione_sociale')
    
    # --- MODIFICA QUI: Questi sono i campi corretti per il raw_id ---
    raw_id_fields = ('cliente', 'fornitore', 'cantiere')
    
    readonly_fields = ('imponibile', 'iva', 'totale', 'created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = [DocumentoRigaInline]
    
    # Non ci servono fieldsets complessi per ora, l'admin gestirà i campi
    # in base a quali sono compilati. Rimuoviamoli per semplicità.

    # --- NUOVO METODO per mostrare il contatto corretto nella lista ---
    @admin.display(description='Contatto')
    def contatto(self, obj):
        if obj.cliente:
            return obj.cliente
        if obj.fornitore:
            return obj.fornitore
        return "-"
    
    class Media:
        js = ('admin/js/documento_form.js',)

    def save_model(self, request, obj, form, change):
        # ... la logica di save_model rimane la stessa di prima ...
        if not obj.pk:
            obj.created_by = request.user
            from django.utils import timezone
            current_year = timezone.now().year
            if obj.tipo_documento == DocumentoTestata.TipoDocumento.FATTURA_VENDITA:
                # ... logica di numerazione ...
                pass
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        # ... la logica di save_formset rimane la stessa di prima ...
        formset.save()
        testata = form.instance
        testata.imponibile = sum(r.imponibile_riga for r in testata.righe.all() if r.imponibile_riga)
        testata.iva = sum(r.iva_riga for r in testata.righe.all() if r.iva_riga)
        testata.totale = testata.imponibile + testata.iva
        testata.save()
        super().save_formset(request, form, formset, change)