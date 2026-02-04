from django.urls import path
from .views import dashboard, landing

app_name = 'dashboard'

urlpatterns = [
    path('', landing, name='landing'),
    path('dashboard/', dashboard, name='dashboard'),
]