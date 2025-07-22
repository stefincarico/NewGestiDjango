from django.contrib import admin
from .models import AliquotaIVA, ModalitaPagamento

# Registra i tuoi modelli qui.

@admin.register(AliquotaIVA)
class AliquotaIVAAdmin(admin.ModelAdmin):
    list_display = ('descrizione', 'valore_percentuale', 'attivo')
    list_filter = ('attivo',)
    search_fields = ('descrizione',)

@admin.register(ModalitaPagamento)
class ModalitaPagamentoAdmin(admin.ModelAdmin):
    list_display = ('descrizione', 'giorni_scadenza', 'attivo')
    list_filter = ('attivo',)
    search_fields = ('descrizione',)