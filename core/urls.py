# audesp_generator/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # A página inicial (URL vazia) aponta para a view 'home'
    path('', views.home, name='home'), # ESSA É A LINHA PRINCIPAL PARA A HOME
    path('documento-fiscal/', views.gerar_xml_documento_fiscal, name='gerar_df'),
    path('pagamento/', views.gerar_xml_pagamento, name='gerar_pg'),
]