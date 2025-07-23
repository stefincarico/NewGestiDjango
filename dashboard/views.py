from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required 
from django.utils import timezone
from core.models import PrimaNota, ContoFinanziario, Scadenza
from django.db.models import Sum, Q, F, DecimalField
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required
def dashboard_view(request):
    oggi = timezone.now().date()

    # --- 1. Calcolo Crediti v/Clienti (Attivo) ---
    crediti = Scadenza.objects.filter(
        tipo_scadenza=Scadenza.TipoScadenza.INCASSO,
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE]
    ).aggregate(
        # Somma di tutti gli importi residui
        totale_crediti=Coalesce(Sum(F('importo') - F('importo_pagato')), 0, output_field=DecimalField()),
        # Somma dei residui solo per le scadenze con data passata
        totale_scaduti=Coalesce(Sum(
            F('importo') - F('importo_pagato'), 
            filter=Q(data_scadenza__lt=oggi)
        ), 0, output_field=DecimalField())
    )

    # --- 2. Calcolo Debiti v/Fornitori (Passivo) ---
    debiti = Scadenza.objects.filter(
        tipo_scadenza=Scadenza.TipoScadenza.PAGAMENTO,
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE]
    ).aggregate(
        totale_debiti=Coalesce(Sum(F('importo') - F('importo_pagato')), 0, output_field=DecimalField()),
        totale_scaduti=Coalesce(Sum(
            F('importo') - F('importo_pagato'),
            filter=Q(data_scadenza__lt=oggi)
        ), 0, output_field=DecimalField())
    )
    
    # --- 3. Calcolo Saldi Conti Finanziari e Liquidità Totale ---
    conti_finanziari = ContoFinanziario.objects.filter(attivo=True).annotate(
        # Per ogni conto, calcola la somma delle entrate e delle uscite
        totale_entrate=Coalesce(Sum('movimenti__importo', filter=Q(movimenti__tipo_movimento='Entrata')), 0, output_field=DecimalField()),
        totale_uscite=Coalesce(Sum('movimenti__importo', filter=Q(movimenti__tipo_movimento='Uscita')), 0, output_field=DecimalField())
    ).annotate(
        # Calcola il saldo come differenza
        saldo=F('totale_entrate') - F('totale_uscite')
    )
    
    liquidita_totale = conti_finanziari.aggregate(totale=Sum('saldo'))['totale'] or 0.00

    # --- 4. Calcoli Finali ---
    crediti_totali = crediti['totale_crediti']
    debiti_totali = debiti['totale_debiti']
    saldo_circolante_netto = crediti_totali - debiti_totali
    
    # --- 5. Dati per i Widget ---
    scadenze_imminenti = Scadenza.objects.filter(        
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE],
        data_scadenza__gte=oggi
        ).order_by('data_scadenza')[:5]
    

    # Inseriamo i dati nel contesto da passare al template
    context = {
        'crediti_totali': crediti_totali,
        'crediti_scaduti': crediti['totale_scaduti'],
        'debiti_totali': debiti_totali,
        'debiti_scaduti': debiti['totale_scaduti'],
        'liquidita_totale': liquidita_totale,
        'saldo_circolante_netto': saldo_circolante_netto,
        'conti_finanziari_con_saldo': conti_finanziari,
        'scadenze_imminenti': scadenze_imminenti,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def scadenziario_incassi_view(request):
    scadenze = Scadenza.objects.filter(
        tipo_scadenza=Scadenza.TipoScadenza.INCASSO,
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE]
    ).order_by('data_scadenza')
    context = {'scadenze': scadenze, 'titolo': 'Scadenziario Incassi'}
    return render(request, 'dashboard/scadenziario_list.html', context)

@login_required
def scadenziario_pagamenti_view(request):
    scadenze = Scadenza.objects.filter(
        tipo_scadenza=Scadenza.TipoScadenza.PAGAMENTO,
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE]
    ).order_by('data_scadenza')
    context = {'scadenze': scadenze, 'titolo': 'Scadenziario Pagamenti'}
    return render(request, 'dashboard/scadenziario_list.html', context)

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

        tipo_movimento_primanota = None
        if scadenza.tipo_scadenza == Scadenza.TipoScadenza.INCASSO:
            tipo_movimento_primanota = PrimaNota.TipoMovimento.ENTRATA
        elif scadenza.tipo_scadenza == Scadenza.TipoScadenza.PAGAMENTO:
            tipo_movimento_primanota = PrimaNota.TipoMovimento.USCITA

        # Crea il movimento di PrimaNota con il tipo corretto
        if tipo_movimento_primanota:
            PrimaNota.objects.create(
                data=data,
                tipo_movimento=tipo_movimento_primanota, # <-- Usa la variabile tradotta
                descrizione=f"SALDO SCAD. DOC. {scadenza.documento.numero_documento}",
                importo=importo,
                conto_finanziario=conto,
                scadenza_collegata=scadenza,
                anagrafica=scadenza.anagrafica
            )
        scadenza.refresh_from_db()
        
    # --- NUOVA LOGICA DI RICALCOLO ---
    # Dopo aver salvato, ricalcoliamo i saldi per la dashboard di tesoreria
    conti_finanziari = ContoFinanziario.objects.filter(attivo=True).annotate(
        totale_entrate=Coalesce(Sum('movimenti__importo', filter=Q(movimenti__tipo_movimento='Entrata')), 0, output_field=DecimalField()),
        totale_uscite=Coalesce(Sum('movimenti__importo', filter=Q(movimenti__tipo_movimento='Uscita')), 0, output_field=DecimalField())
    ).annotate(saldo=F('totale_entrate') - F('totale_uscite'))
    
    liquidita_totale = conti_finanziari.aggregate(totale=Sum('saldo'))['totale'] or 0.00

    context = {
        'scadenza': scadenza, # La scadenza appena aggiornata
        'conti': conti_finanziari, # I conti con i nuovi saldi
        'liquidita_totale': liquidita_totale
    }
    
    # Restituisce un nuovo template che contiene più pezzi
    return render(request, 'dashboard/partials/pagamento_success.html', context)

@login_required
def get_scadenza_row(request, scadenza_id):
    scadenza = get_object_or_404(Scadenza, pk=scadenza_id)
    # Questa vista restituisce una singola riga aggiornata (utile per l'annulla).
    return render(request, 'dashboard/partials/riga_scadenza.html', {'scadenza': scadenza})

@login_required
def scadenziario_view(request):
    scadenze_list = Scadenza.objects.filter(
        stato__in=[Scadenza.StatoScadenza.APERTA, Scadenza.StatoScadenza.PAGATA_PARZIALMENTE]
    ).select_related('documento').prefetch_related('anagrafica').order_by('data_scadenza')

    # --- Calcolo KPI con la logica corretta a livello di DB ---
    kpi = scadenze_list.aggregate(
        tot_incassi=Coalesce(Sum(F('importo') - F('importo_pagato'), filter=Q(tipo_scadenza='Incasso')), 0, output_field=DecimalField()),
        tot_pagamenti=Coalesce(Sum(F('importo') - F('importo_pagato'), filter=Q(tipo_scadenza='Pagamento')), 0, output_field=DecimalField())
    )
    kpi['saldo_circolante'] = kpi['tot_incassi'] - kpi['tot_pagamenti']

    # --- Logica di Paginazione (invariata) ---
    paginator = Paginator(scadenze_list, 15)
    page_number = request.GET.get('page')
    try:
        scadenze_page = paginator.page(page_number)
    except PageNotAnInteger:
        scadenze_page = paginator.page(1)
    except EmptyPage:
        scadenze_page = paginator.page(paginator.num_pages)

    context = {
        'scadenze': scadenze_page,
        'kpi': kpi,
        'titolo': 'Scadenziario Aperto'
    }
    return render(request, 'dashboard/scadenziario_list.html', context)

@login_required
def tesoreria_view(request):
    """
    Mostra i saldi di tutti i conti finanziari.
    """
    # Riutilizziamo la potente query con annotate che abbiamo già scritto!
    conti_finanziari = ContoFinanziario.objects.filter(attivo=True).annotate(
        totale_entrate=Coalesce(Sum('movimenti__importo', filter=Q(movimenti__tipo_movimento='Entrata')), 0, output_field=DecimalField()),
        totale_uscite=Coalesce(Sum('movimenti__importo', filter=Q(movimenti__tipo_movimento='Uscita')), 0, output_field=DecimalField())
    ).annotate(
        saldo=F('totale_entrate') - F('totale_uscite')
    )
    
    # Calcoliamo la liquidità totale da passare al template
    liquidita_totale = conti_finanziari.aggregate(totale=Sum('saldo'))['totale'] or 0.00

    context = {
        'conti': conti_finanziari,
        'liquidita_totale': liquidita_totale,
        'data_oggi': timezone.now().date(),
        'titolo': 'Dashboard Tesoreria'
    }
    
    return render(request, 'dashboard/tesoreria.html', context)