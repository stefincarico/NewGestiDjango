from django.contrib.contenttypes.admin import GenericTabularInline 
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

# 1. Definiamo l'inline per le righe del documento
class DocumentoRigaInline(admin.TabularInline):
    model = DocumentoRiga
    # fields = ['descrizione', 'quantita', 'prezzo_unitario', 'aliquota_iva'] # Campi da mostrare
    readonly_fields = ('imponibile_riga', 'iva_riga') # Mostra i totali di riga ma non li rende modificabili
    extra = 1 # Mostra sempre una riga vuota per l'inserimento

#@admin.register(DocumentoTestata)
class DocumentoTestataAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'content_object', 'stato', 'totale')
    list_filter = ('stato', 'tipo_documento', 'data_documento')
    search_fields = ('numero_documento',) 
    
    readonly_fields = ('imponibile', 'iva', 'totale', 'numero_documento', 'created_at', 'updated_at', 'created_by', 'updated_by')
    inlines = [DocumentoRigaInline]

    fieldsets = (
        ('Informazioni Principali', {
            'fields': (
                ('tipo_documento', 'stato'),
                ('numero_documento', 'data_documento'),
                # Questi due ora verranno manipolati via JS
                'content_type', 
                'object_id',
                'cantiere', 
                'modalita_pagamento'
            )
        }),
        ('Riepilogo', {
            'classes': ('collapse',),
            'fields': ('imponibile', 'iva', 'totale')
        }),
        ('Note', {
            'fields': ('note',)
        }),
    )

    class Media:
        js = ('admin/js/documento_form.js',)

    # Rimuoviamo il metodo get_form, non serve per questa logica.
    
    def get_readonly_fields(self, request, obj=None):
        # Se l'oggetto esiste già, rendiamo il numero documento non modificabile
        if obj:
            # Aggiunge 'numero_documento' ai readonly_fields standard in modalità modifica
            return self.readonly_fields + ('numero_documento',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
            
            from django.utils import timezone
            current_year = timezone.now().year
            
            if obj.tipo_documento == DocumentoTestata.TipoDocumento.FATTURA_VENDITA:
                last_doc = DocumentoTestata.objects.filter(
                    tipo_documento=obj.tipo_documento,
                    data_documento__year=current_year
                ).order_by('numero_documento').last()
                
                new_number = 1
                if last_doc and last_doc.numero_documento.startswith(f"FT-{current_year}-"):
                    try:
                        new_number = int(last_doc.numero_documento.split('-')[-1]) + 1
                    except (ValueError, IndexError):
                        pass
                obj.numero_documento = f"FT-{current_year}-{new_number:06d}"

        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    # ... save_formset rimane identico ...
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        
        testata = form.instance
        testata.imponibile = sum(riga.imponibile_riga for riga in testata.righe.all())
        testata.iva = sum(riga.iva_riga for riga in testata.righe.all())
        testata.totale = testata.imponibile + testata.iva
        testata.save()
        super().save_formset(request, form, formset, change)