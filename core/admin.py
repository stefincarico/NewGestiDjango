from django.contrib import admin
from .models import (
    AliquotaIVA, ModalitaPagamento,
    Cliente, Fornitore, Dipendente,
    Cantiere, DocumentoTestata, DocumentoRiga, Scadenza, PrimaNota,
    ContoFinanziario, ContoOperativo
)

# ==============================================================================
# === MODELLI DI CONFIGURAZIONE E ANAGRAFICHE (Logica semplice)              ===
# ==============================================================================

@admin.register(AliquotaIVA)
class AliquotaIVAAdmin(admin.ModelAdmin):
    list_display = ('descrizione', 'valore_percentuale', 'attivo')
    exclude = ('created_by', 'updated_by')
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ModalitaPagamento)
class ModalitaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('descrizione', 'giorni_scadenza', 'attivo')
    exclude = ('created_by', 'updated_by')
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_cognome_ragione_sociale', 'partita_iva', 'citta', 'attivo')
    search_fields = ('nome_cognome_ragione_sociale', 'partita_iva', 'codice_fiscale')
    exclude = ('created_by', 'updated_by')
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Fornitore)
class FornitoreAdmin(admin.ModelAdmin):
    list_display = ('nome_cognome_ragione_sociale', 'partita_iva', 'citta', 'attivo')
    search_fields = ('nome_cognome_ragione_sociale', 'partita_iva', 'codice_fiscale')
    exclude = ('created_by', 'updated_by')
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Dipendente)
class DipendenteAdmin(admin.ModelAdmin):
    list_display = ('nome_cognome_ragione_sociale', 'mansione', 'attivo')
    search_fields = ('nome_cognome_ragione_sociale', 'mansione')
    exclude = ('created_by', 'updated_by')
    fieldsets = (
        ('Dati Anagrafici', {'fields': ('nome_cognome_ragione_sociale', ('codice_fiscale', 'partita_iva'), 'attivo')}),
        ('Dati di Contatto', {'fields': ('indirizzo', 'cap', 'citta', 'provincia', 'email', 'telefono')}),
        ('Dati Lavorativi', {'fields': ('mansione', 'data_assunzione', 'data_fine_rapporto', 'costo_orario', 'note_generali')}),
    )
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(Cantiere)
class CantiereAdmin(admin.ModelAdmin):
    list_display = ('codice_cantiere', 'descrizione', 'cliente', 'stato')
    search_fields = ('codice_cantiere', 'descrizione', 'cliente__nome_cognome_ragione_sociale')
    raw_id_fields = ('cliente',) # Migliora la selezione del cliente
    exclude = ('created_by', 'updated_by')
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

# ==============================================================================
# === DOCUMENTI (Logica avanzata)                                            ===
# ==============================================================================

class DocumentoRigaInline(admin.TabularInline):
    model = DocumentoRiga
    readonly_fields = ('imponibile_riga', 'iva_riga')
    extra = 1

@admin.register(DocumentoTestata)
class DocumentoTestataAdmin(admin.ModelAdmin):
    # --- 1. CONFIGURAZIONE LISTA ---
    list_display = ('numero_documento', 'tipo_documento', 'data_documento', 'contatto', 'stato', 'totale')
    list_display_links = ('numero_documento',)
    list_filter = ('stato', 'tipo_documento', 'data_documento')
    search_fields = ('numero_documento', 'cliente__nome_cognome_ragione_sociale', 'fornitore__nome_cognome_ragione_sociale')
    inlines = [DocumentoRigaInline]

    # --- 2. CONFIGURAZIONE FORM ---
    raw_id_fields = ('cliente', 'fornitore', 'cantiere')
    # Campi che non devono mai essere modificati a mano nel form
    readonly_fields = ('imponibile', 'iva', 'totale', 'created_at', 'updated_at', 'created_by', 'updated_by')

    # Carica il nostro JavaScript per rendere il form dinamico
    class Media:
        js = ('admin/js/documento_form.js',)
        
    # Organizza i campi nel form
    fieldsets = (
        ('Informazioni Principali', {
            'fields': (
                ('tipo_documento', 'stato'),
                ('numero_documento', 'data_documento'),
                'cliente', 
                'fornitore',
                'cantiere', 
                'modalita_pagamento'
            )
        }),
        ('Riepilogo', {'classes': ('collapse',), 'fields': ('imponibile', 'iva', 'totale')}),
        ('Note', {'fields': ('note',)}),
    )

    # --- 3. METODI PER LOGICA PERSONALIZZATA ---
    
    # Metodo per mostrare il contatto corretto nella lista
    @admin.display(description='Contatto')
    def contatto(self, obj):
        if obj.cliente: return obj.cliente
        if obj.fornitore: return obj.fornitore
        return "-"

    # Rende il campo 'numero_documento' readonly solo in modifica
    def get_readonly_fields(self, request, obj=None):
        if obj: # Se stiamo modificando un oggetto
            return self.readonly_fields + ('numero_documento',)
        return self.readonly_fields

    # Logica di salvataggio per audit e numerazione automatica
    def save_model(self, request, obj, form, change):
        obj.updated_by = request.user
        if not obj.pk: # In creazione...
            obj.created_by = request.user
            doc_type = obj.tipo_documento
            if doc_type in [DocumentoTestata.TipoDocumento.FATTURA_VENDITA, DocumentoTestata.TipoDocumento.NOTA_CREDITO_VENDITA]:
                from django.utils import timezone
                current_year = timezone.now().year
                prefix = f"FT-{current_year}-" if doc_type == DocumentoTestata.TipoDocumento.FATTURA_VENDITA else f"NC-{current_year}-"
                last_doc = DocumentoTestata.objects.filter(tipo_documento=doc_type, data_documento__year=current_year).order_by('numero_documento').last()
                new_number = 1
                if last_doc and last_doc.numero_documento.startswith(prefix):
                    try:
                        new_number = int(last_doc.numero_documento.replace(prefix, '')) + 1
                    except (ValueError, IndexError): pass
                obj.numero_documento = f"{prefix}{new_number:06d}"
        
        # Per i documenti di acquisto, normalizziamo il numero inserito manualmente
        elif obj.numero_documento:
            obj.numero_documento = obj.numero_documento.upper()

        super().save_model(request, obj, form, change)

    # Ricalcola i totali della testata dopo aver salvato le righe
    def save_formset(self, request, form, formset, change):
        formset.save()
        testata = form.instance
        testata.imponibile = sum(r.imponibile_riga for r in testata.righe.all() if r.imponibile_riga is not None)
        testata.iva = sum(r.iva_riga for r in testata.righe.all() if r.iva_riga is not None)
        testata.totale = testata.imponibile + testata.iva
        testata.save()

# ==============================================================================
# === CONTABILITA' E TESORERIA                                               ===
# ==============================================================================

@admin.register(Scadenza)
class ScadenzaAdmin(admin.ModelAdmin):
    list_display = ('data_scadenza', 'anagrafica', 'importo', 'importo_residuo', 'stato', 'documento', 'is_scaduta')
    list_filter = ('stato', 'tipo_scadenza', 'data_scadenza')
    search_fields = ('documento__numero_documento',)
    readonly_fields = ('importo_residuo', 'is_scaduta', 'created_at', 'updated_at', 'created_by', 'updated_by')

@admin.register(ContoFinanziario)
class ContoFinanziarioAdmin(admin.ModelAdmin):
    list_display = ('nome_conto', 'attivo')
    exclude = ('created_by', 'updated_by')
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(ContoOperativo)
class ContoOperativoAdmin(admin.ModelAdmin):
    list_display = ('nome_conto', 'tipo', 'attivo')
    list_filter = ('tipo', 'attivo')
    exclude = ('created_by', 'updated_by')
    def save_model(self, request, obj, form, change):
        if not obj.pk: obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(PrimaNota)
class PrimaNotaAdmin(admin.ModelAdmin):
    list_display = ('data', 'descrizione', 'importo', 'tipo_movimento', 'conto_finanziario', 'scadenza_collegata')
    list_filter = ('tipo_movimento', 'data', 'conto_finanziario')
    raw_id_fields = ('scadenza_collegata', 'anagrafica', 'cantiere')
    fieldsets = (
        ('Dati Principali', {'fields': (('data', 'tipo_movimento'),'descrizione',('importo', 'conto_finanziario'))}),
        ('Collegamenti (Opzionali)', {'classes': ('collapse',),'fields': ('scadenza_collegata','conto_operativo','anagrafica','cantiere')}),
    )