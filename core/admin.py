from django.contrib import admin
from .models import AliquotaIVA, ModalitaPagamento

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