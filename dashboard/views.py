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