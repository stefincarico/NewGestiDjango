# in core/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import DocumentoTestata, Scadenza, PrimaNota
from datetime import timedelta
from django.db.models import Sum 

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

def aggiorna_stato_scadenza(scadenza_id):
    """
    Funzione helper per ricalcolare e aggiornare una singola scadenza.
    Questa è la logica centrale che verrà richiamata dai segnali.
    """
    try:
        scadenza = Scadenza.objects.get(pk=scadenza_id)
        
        # Calcola la somma di tutti i pagamenti collegati usando un'aggregazione
        totale_pagato = scadenza.pagamenti.aggregate(totale=Sum('importo'))['totale'] or 0.00
        
        scadenza.importo_pagato = totale_pagato
        
        # Aggiorna lo stato in base al totale pagato
        if totale_pagato >= scadenza.importo:
            scadenza.stato = Scadenza.StatoScadenza.SALDATA
        elif totale_pagato > 0:
            scadenza.stato = Scadenza.StatoScadenza.PAGATA_PARZIALMENTE
        else:
            scadenza.stato = Scadenza.StatoScadenza.APERTA
            
        scadenza.save(update_fields=['importo_pagato', 'stato'])

    except Scadenza.DoesNotExist:
        pass # La scadenza potrebbe essere stata cancellata, non facciamo nulla.

@receiver(post_save, sender=PrimaNota)
def gestisci_pagamento_salvato(sender, instance, **kwargs):
    """ Eseguito dopo che un movimento di PrimaNota viene salvato. """
    if instance.scadenza_collegata_id:
        aggiorna_stato_scadenza(instance.scadenza_collegata_id)

@receiver(post_delete, sender=PrimaNota)
def gestisci_pagamento_cancellato(sender, instance, **kwargs):
    """ Eseguito dopo che un movimento di PrimaNota viene cancellato. """
    if instance.scadenza_collegata_id:
        aggiorna_stato_scadenza(instance.scadenza_collegata_id)

