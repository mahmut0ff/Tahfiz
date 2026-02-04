from django.urls import path
from .views import *

app_name = 'schedule'

urlpatterns = [
    path('', schedule, name='list'),
    path('calendar/', calendar_view, name='calendar'),
    path('<int:pk>/delete/', delete, name='delete'),
    path('subjects/create/', subject_create, name='subject_create'),
]