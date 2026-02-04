from django.urls import path
from .views import *

app_name = 'administrator'

urlpatterns = [
    path('', list, name='list'),
    path('create/', create, name='create'),
    path('<int:pk>/', details, name='details'),
    path('<int:pk>/delete/', delete, name='delete'),
]