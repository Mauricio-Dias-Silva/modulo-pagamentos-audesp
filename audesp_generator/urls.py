# audesp_generator/urls.py (o principal)
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # <--- ESSA LINHA PRECISA ESTAR AQUI
]