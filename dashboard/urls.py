# in dashboard/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views 
from .views import (
    dashboard_view, scadenziario_incassi_view, scadenziario_pagamenti_view, 
    registra_pagamento_form, salva_pagamento, get_scadenza_row,scadenziario_view
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('scadenziario/', scadenziario_view, name='scadenziario'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('scadenza/<int:scadenza_id>/registra-pagamento/', registra_pagamento_form, name='registra_pagamento_form'),
    path('scadenza/<int:scadenza_id>/registra-pagamento/', registra_pagamento_form, name='registra_pagamento_form'),
    path('scadenza/<int:scadenza_id>/salva-pagamento/', salva_pagamento, name='salva_pagamento'),
    path('scadenza/<int:scadenza_id>/', get_scadenza_row, name='get_scadenza_row'),
]