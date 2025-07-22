from django.db import models
from django.conf import settings

# NOTA: Questo è il nostro modello base astratto per non ripetere il codice.
class TenantBaseModel(models.Model):
    attivo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        abstract = True # Dice a Django di non creare una tabella per questo modello.

# --- Iniziamo con alcune semplici tabelle di configurazione ---

class AliquotaIVA(TenantBaseModel):
    descrizione = models.CharField(max_length=100, unique=True)
    valore_percentuale = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Valore in percentuale (es. 22.00)"
    )

    def __str__(self):
        return f"{self.descrizione} ({self.valore_percentuale}%)"

    class Meta:
        verbose_name = "Aliquota IVA"
        verbose_name_plural = "Aliquote IVA"


class ModalitaPagamento(TenantBaseModel):
    descrizione = models.CharField(max_length=100, unique=True)
    giorni_scadenza = models.PositiveIntegerField(default=0, help_text="Giorni dalla data del documento per la scadenza (0 per immediato).")

    def __str__(self):
        return self.descrizione

    class Meta:
        verbose_name = "Modalità di Pagamento"
        verbose_name_plural = "Modalità di Pagamento"