from django.shortcuts import render
from django.contrib.auth.decorators import login_required 

# Create your views here.

@login_required
def dashboard_view(request):
    # Per ora, questa vista fa solo una cosa: mostra la pagina della dashboard.
    # In futuro, qui recupereremo i dati da passare al template.
    return render(request, 'dashboard/dashboard.html')