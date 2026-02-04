from django.urls import path
from . import views

app_name = 'graduate'

urlpatterns = [
    path('', views.graduate_list, name='list'),
    path('<int:pk>/', views.graduate_detail, name='detail'),
    path('create/', views.graduate_create, name='create'),
    path('<int:pk>/update/', views.graduate_update, name='update'),
    path('<int:pk>/delete/', views.graduate_delete, name='delete'),
    path('<int:graduate_pk>/achievement/create/', views.achievement_create, name='achievement_create'),
    path('achievement/<int:pk>/delete/', views.achievement_delete, name='achievement_delete'),
    path('make-graduate/<int:student_pk>/', views.make_graduate, name='make_graduate'),
]