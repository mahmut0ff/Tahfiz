from django.urls import path
from .views import *

app_name = 'group'

urlpatterns = [
    path('', list, name='list'),
    path('create/', create, name='create'),
    path('<str:pk>/', details, name='details'),
    path('<str:pk>/update/', update, name='update'),
    path('<str:pk>/delete/', delete, name='delete'),
]