from django.shortcuts import render
from django.contrib.auth.decorators import login_required 
from django.utils import timezone
from django.shortcuts import get_object_or_404
from core.models import PrimaNota, ContoFinanziario, Scadenza

# Create your views here.

@login_required
def dashboard_view(request):
    oggi = timezone.now().date()
    
    # Recupera le prossime 10 scadenze di INCASSO non ancora saldate
    scadenze_in_entrata = Scadenza.objects.filter(
        tipo_scadenza=Scadenza.TipoScadenza.INCASSO,
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE]
    ).order_by('data_scadenza')[:10] # Ordina per data e prendi le prime 10

    context = {
        'scadenze_in_entrata': scadenze_in_entrata
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def registra_pagamento_form(request, scadenza_id):
    scadenza = get_object_or_404(Scadenza, pk=scadenza_id)
    
    # Dati iniziali per il form di PrimaNota
    initial_data = {
        'tipo_movimento': scadenza.tipo_scadenza,
        'descrizione': f"SALDO SCAD. DOC. {scadenza.documento.numero_documento}",
        'importo': scadenza.importo_residuo,
        'data': timezone.now().date(),
    }
    
    # Qui in futuro useremo un Django Form per validazione.
    # Per ora, passiamo i dati e la lista dei conti.
    context = {
        'scadenza': scadenza,
        'initial_data': initial_data,
        'conti_finanziari': ContoFinanziario.objects.filter(attivo=True)
    }
    # NOTA: Restituiamo un template "parziale", senza estendere base.html
    return render(request, 'dashboard/partials/form_pagamento.html', context)

@login_required
def salva_pagamento(request, scadenza_id):
    scadenza = get_object_or_404(Scadenza, pk=scadenza_id)
    if request.method == 'POST':
        # Recupera i dati inviati dal form
        importo = request.POST.get('importo')
        conto_id = request.POST.get('conto_finanziario')
        data = request.POST.get('data')
        conto = get_object_or_404(ContoFinanziario, pk=conto_id)

        # Crea il movimento di PrimaNota (questo attiverà i nostri segnali!)
        PrimaNota.objects.create(
            data=data,
            tipo_movimento=scadenza.tipo_scadenza,
            descrizione=f"SALDO SCAD. DOC. {scadenza.documento.numero_documento}",
            importo=importo,
            conto_finanziario=conto,
            scadenza_collegata=scadenza,
            anagrafica=scadenza.anagrafica
        )
        # Ricarica la scadenza dal DB per avere i dati aggiornati dal segnale
        scadenza.refresh_from_db()
        
    # Restituisce solo la riga della tabella aggiornata
    return render(request, 'dashboard/partials/riga_scadenza.html', {'scadenza': scadenza})

@login_required
def get_scadenza_row(request, scadenza_id):
    scadenza = get_object_or_404(Scadenza, pk=scadenza_id)
    return render(request, 'dashboard/partials/riga_scadenza.html', {'scadenza': scadenza})