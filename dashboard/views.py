from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.utils import timezone
from core.models import PrimaNota, ContoFinanziario, Scadenza

@login_required
def dashboard_view(request):
    scadenze_in_entrata = Scadenza.objects.filter(
        tipo_scadenza=Scadenza.TipoScadenza.INCASSO,
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE]
    ).order_by('data_scadenza')[:10]

    context = {'scadenze_in_entrata': scadenze_in_entrata}
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def registra_pagamento_form(request, scadenza_id):
    scadenza = get_object_or_404(Scadenza, pk=scadenza_id)
    initial_data = {
        'tipo_movimento': scadenza.tipo_scadenza,
        'descrizione': f"SALDO SCAD. DOC. {scadenza.documento.numero_documento}",
        'importo': scadenza.importo_residuo,
        'data': timezone.now().date(),
    }
    context = {
        'scadenza': scadenza,
        'initial_data': initial_data,
        'conti_finanziari': ContoFinanziario.objects.filter(attivo=True)
    }
    return render(request, 'dashboard/partials/form_pagamento.html', context)

@login_required
def salva_pagamento(request, scadenza_id):
    scadenza = get_object_or_404(Scadenza, pk=scadenza_id)
    if request.method == 'POST':
        importo = request.POST.get('importo')
        conto_id = request.POST.get('conto_finanziario')
        data = request.POST.get('data')
        conto = get_object_or_404(ContoFinanziario, pk=conto_id)

        PrimaNota.objects.create(
            data=data,
            tipo_movimento=scadenza.tipo_scadenza,
            descrizione=f"SALDO SCAD. DOC. {scadenza.documento.numero_documento}",
            importo=importo,
            conto_finanziario=conto,
            scadenza_collegata=scadenza,
            anagrafica=scadenza.anagrafica
        )
        scadenza.refresh_from_db()
        
    # Dopo aver salvato, restituisce la riga della tabella aggiornata.
    return render(request, 'dashboard/partials/riga_scadenza.html', {'scadenza': scadenza})

@login_required
def get_scadenza_row(request, scadenza_id):
    scadenza = get_object_or_404(Scadenza, pk=scadenza_id)
    # Questa vista restituisce una singola riga aggiornata (utile per l'annulla).
    return render(request, 'dashboard/partials/riga_scadenza.html', {'scadenza': scadenza})

