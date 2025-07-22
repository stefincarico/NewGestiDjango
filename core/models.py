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

# === ANAGRAFICHE ===
# Questo è il modello genitore che contiene tutti i campi comuni.

class Anagrafica(TenantBaseModel):
    nome_cognome_ragione_sociale = models.CharField(max_length=255)
    codice_fiscale = models.CharField(max_length=16, blank=True, help_text="Valido sia per persone fisiche che giuridiche")
    partita_iva = models.CharField(max_length=11, blank=True)

    # Indirizzo
    indirizzo = models.CharField(max_length=255, blank=True)
    cap = models.CharField(max_length=5, blank=True)
    citta = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=2, blank=True)

    # Contatti
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=50, blank=True)

    def save(self, *args, **kwargs):
        # Normalizzazione dei campi prima di salvare
        self.nome_cognome_ragione_sociale = self.nome_cognome_ragione_sociale.upper()
        if self.codice_fiscale:
            self.codice_fiscale = self.codice_fiscale.upper()
        if self.indirizzo:
            self.indirizzo = self.indirizzo.title()
        if self.citta:
            self.citta = self.citta.title()
        if self.provincia:
            self.provincia = self.provincia.upper()
        
        super().save(*args, **kwargs) # Chiama il metodo save() originale per salvare effettivamente   
        
    class Meta:
        verbose_name = "Anagrafica"
        verbose_name_plural = "Tutte le Anagrafiche"

    def __str__(self):
        return self.nome_cognome_ragione_sociale


# --- Modelli Figli ---
# Ognuno eredita tutti i campi da Anagrafica e aggiunge i suoi specifici.

class Cliente(Anagrafica):
    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clienti"


class Fornitore(Anagrafica):
    class Meta:
        verbose_name = "Fornitore"
        verbose_name_plural = "Fornitori"


class Dipendente(Anagrafica):
    # Qui mettiamo i campi che erano in 'DipendenteDettaglio'
    mansione = models.CharField(max_length=255)
    data_assunzione = models.DateField()
    data_fine_rapporto = models.DateField(null=True, blank=True)
    costo_orario = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    note_generali = models.TextField(blank=True)

    class Meta:
        verbose_name = "Dipendente"
        verbose_name_plural = "Dipendenti"