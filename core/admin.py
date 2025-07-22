from django.contrib import admin
from .models import (
    AliquotaIVA, ModalitaPagamento,
    Cliente, Fornitore, Dipendente
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