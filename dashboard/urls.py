# in dashboard/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views 
from .views import dashboard_view, registra_pagamento_form

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('scadenza/<int:scadenza_id>/registra-pagamento/', registra_pagamento_form, name='registra_pagamento_form'),
]