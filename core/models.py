from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class TenantBaseModel(models.Model):
    attivo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        abstract = True # Dice a Django di non creare una tabella per questo modello.

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

# === CANTIERI / PROGETTI ===
class Cantiere(TenantBaseModel):
    class Stato(models.TextChoices):
        BOZZA = 'Bozza', 'Bozza'
        APERTO = 'Aperto', 'Aperto'
        SOSPESO = 'Sospeso', 'Sospeso'
        CHIUSO = 'Chiuso', 'Chiuso'
        ANNULLATO = 'Annullato', 'Annullato'

    codice_cantiere = models.CharField(
        max_length=50,  # Aumentiamo un po' la lunghezza
        unique=True, 
        help_text="Es. C-2025-ROMA-001"
    )
    descrizione = models.CharField(max_length=255)
    indirizzo = models.CharField(max_length=255, blank=True)

    # La relazione chiave!
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT, 
        help_text="Il cliente a cui è associato il cantiere"
    )

    data_inizio = models.DateField(null=True, blank=True)
    data_fine_prevista = models.DateField(null=True, blank=True)
    data_chiusura_effettiva = models.DateField(null=True, blank=True)
    
    stato = models.CharField(max_length=20, choices=Stato.choices, default=Stato.BOZZA)

    def __str__(self):
        return f"[{self.codice_cantiere}] {self.descrizione}"

    def save(self, *args, **kwargs):
        self.codice_cantiere = self.codice_cantiere.upper()
        self.descrizione = self.descrizione.upper()
        if self.indirizzo:
            self.indirizzo = self.indirizzo.title()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Cantiere"
        verbose_name_plural = "Cantieri"
        ordering = ['-data_inizio']
# === DOCUMENTI (FATTURAZIONE) - VERSIONE SCALABILE ===

class DocumentoTestata(TenantBaseModel):
    class TipoDocumento(models.TextChoices):
        FATTURA_VENDITA = 'FatturaVendita', 'Fattura di Vendita'
        NOTA_CREDITO_VENDITA = 'NotaCreditoVendita', 'Nota di Credito di Vendita'
        FATTURA_ACQUISTO = 'FatturaAcquisto', 'Fattura di Acquisto'
        NOTA_CREDITO_ACQUISTO = 'NotaCreditoAcquisto', 'Nota di Credito di Acquisto'
    
    class StatoDocumento(models.TextChoices):
        BOZZA = 'Bozza', 'Bozza'
        CONFERMATO = 'Confermato', 'Confermato'
        ANNULLATO = 'Annullato', 'Annullato'

    tipo_documento = models.CharField(max_length=30, choices=TipoDocumento.choices)
    stato = models.CharField(max_length=20, choices=StatoDocumento.choices, default=StatoDocumento.BOZZA)
    
    # --- LA STRUTTURA CORRETTA E ROBUSTA ---
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='documenti_cliente', null=True, blank=True)
    fornitore = models.ForeignKey(Fornitore, on_delete=models.PROTECT, related_name='documenti_fornitore', null=True, blank=True)
    
    cantiere = models.ForeignKey(Cantiere, on_delete=models.PROTECT, related_name='documenti', null=True, blank=True)
    modalita_pagamento = models.ForeignKey(ModalitaPagamento, on_delete=models.PROTECT, null=True, blank=True)

    numero_documento = models.CharField(max_length=50)
    data_documento = models.DateField()
    
    imponibile = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    totale = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_tipo_documento_display()} N. {self.numero_documento} del {self.data_documento}"

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documenti"

class DocumentoRiga(models.Model):
    testata = models.ForeignKey(DocumentoTestata, on_delete=models.CASCADE, related_name='righe')
    
    descrizione = models.CharField(max_length=255)
    quantita = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    prezzo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    aliquota_iva = models.ForeignKey(AliquotaIVA, on_delete=models.PROTECT)

    imponibile_riga = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    iva_riga = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)
    
    def __str__(self):
        return self.descrizione

    def save(self, *args, **kwargs):
        self.descrizione = self.descrizione.upper()
        self.imponibile_riga = self.quantita * self.prezzo_unitario
        moltiplicatore_iva = self.aliquota_iva.valore_percentuale / 100
        self.iva_riga = self.imponibile_riga * moltiplicatore_iva
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Riga Documento"
        verbose_name_plural = "Righe Documento"

# === SCADENZIARIO ===

class Scadenza(TenantBaseModel):
    class TipoScadenza(models.TextChoices):
        INCASSO = 'Incasso', 'Incasso (da Cliente)'
        PAGAMENTO = 'Pagamento', 'Pagamento (a Fornitore)'

    class StatoScadenza(models.TextChoices):
        APERTA = 'Aperta', 'Aperta'
        PAGATA_PARZIALMENTE = 'Parziale', 'Pagata Parzialmente'
        SALDATA = 'Saldata', 'Saldata'
        ANNULLATA = 'Annullata', 'Annullata'

    # Collegamento al documento che ha generato la scadenza
    documento = models.ForeignKey(DocumentoTestata, on_delete=models.CASCADE, related_name='scadenze')
    
    # Relazione generica per sapere a chi si riferisce la scadenza (cliente o fornitore)
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    anagrafica = GenericForeignKey('content_type', 'object_id')

    # Campi descrittivi
    tipo_scadenza = models.CharField(max_length=20, choices=TipoScadenza.choices)
    stato = models.CharField(max_length=20, choices=StatoScadenza.choices, default=StatoScadenza.APERTA)
    
    # Campi economici
    data_scadenza = models.DateField()
    importo = models.DecimalField(max_digits=10, decimal_places=2)
    importo_pagato = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    note = models.TextField(blank=True)
    
    # --- Campi Calcolati (Properties) ---
    
    @property
    def importo_residuo(self):
        """Calcola al volo l'importo ancora da saldare."""
        return self.importo - self.importo_pagato
        
    @property
    def is_scaduta(self):
        """Restituisce True se la data di scadenza è passata e non è ancora saldata."""
        from django.utils import timezone
        oggi = timezone.now().date()
        stati_aperti = [self.StatoScadenza.APERTA, self.StatoScadenza.PAGATA_PARZIALMENTE]
        
        if self.data_scadenza < oggi and self.stato in stati_aperti:
            return True
        return False

    # --- Rappresentazione e Ordinamento ---

    def __str__(self):
        return f"{self.get_tipo_scadenza_display()} di {self.importo} EUR del {self.data_scadenza}"

    class Meta:
        verbose_name = "Scadenza"
        verbose_name_plural = "Scadenze"
        ordering = ['data_scadenza']

