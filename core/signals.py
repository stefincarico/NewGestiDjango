# in core/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import DocumentoTestata, Scadenza
from datetime import timedelta

# Il decoratore @receiver collega la nostra funzione al segnale post_save
# proveniente dal modello DocumentoTestata.
@receiver(post_save, sender=DocumentoTestata)
def crea_o_aggiorna_scadenze(sender, instance, created, **kwargs):
    """
    Questa funzione viene eseguita ogni volta che un DocumentoTestata viene salvato.
    """
    
    # 'instance' è l'oggetto DocumentoTestata che è stato appena salvato.
    documento = instance

    # Vogliamo agire solo se il documento è CONFERMATO.
    # Se è ancora in Bozza o Annullato, non facciamo nulla.
    if documento.stato != DocumentoTestata.StatoDocumento.CONFERMATO:
        # Se ci sono scadenze vecchie e il doc non è più confermato, le annulliamo.
        documento.scadenze.update(stato=Scadenza.StatoScadenza.ANNULLATA)
        return

    # --- Logica di creazione/aggiornamento ---
    # Per ora, implementiamo la logica semplice: una singola scadenza per il totale.
    
    # Eliminiamo le scadenze esistenti per ricrearle (logica semplice per ora)
    documento.scadenze.all().delete()

    if documento.modalita_pagamento and documento.totale > 0:
        # Calcola la data di scadenza
        giorni_scadenza = documento.modalita_pagamento.giorni_scadenza
        data_scadenza = documento.data_documento + timedelta(days=giorni_scadenza)

        # Determina il tipo di scadenza e l'anagrafica corretta
        anagrafica_collegata = None
        tipo_scadenza = None

        if documento.tipo_documento in [DocumentoTestata.TipoDocumento.FATTURA_VENDITA, DocumentoTestata.TipoDocumento.NOTA_CREDITO_ACQUISTO]:
            tipo_scadenza = Scadenza.TipoScadenza.INCASSO
            anagrafica_collegata = documento.cliente
        
        elif documento.tipo_documento in [DocumentoTestata.TipoDocumento.FATTURA_ACQUISTO, DocumentoTestata.TipoDocumento.NOTA_CREDITO_VENDITA]:
            tipo_scadenza = Scadenza.TipoScadenza.PAGAMENTO
            anagrafica_collegata = documento.fornitore
        
        # Crea la nuova scadenza se abbiamo tutte le info
        if anagrafica_collegata and tipo_scadenza:
            Scadenza.objects.create(
                documento=documento,
                anagrafica=anagrafica_collegata,
                tipo_scadenza=tipo_scadenza,
                data_scadenza=data_scadenza,
                importo=documento.totale
            )