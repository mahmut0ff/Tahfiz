from django.urls import path
from .views import *

app_name = 'grade'

urlpatterns = [
    path('groups/', group_list, name='group_list'),
    path('groups/<int:pk>/subjects/', subject_list, name='subject_list'),
    path('groups/<int:group_pk>/subjects/<int:subject_pk>/', grade_list, name='list'),
    path('diary/', diary, name='diary'),
    path('groups/<int:group_pk>/subjects/<int:subject_pk>/<int:pk>/delete/', delete, name='delete'),
]