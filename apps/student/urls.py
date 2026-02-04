from django.urls import path
from .views import *

app_name = 'student'

urlpatterns = [
    path('', list, name='list'),
    path('create/', create, name='create'),
    path('<int:pk>/', details, name='details'),
    path('<int:pk>/delete/', delete, name='delete'),
    path('rating/', choose_course_rating, name='choose_course_rating'),
    path('rating/<int:pk>/', rating_by_course, name='rating_by_course'),
    path('rating/total/', total_rating_list, name='total_rating_list'),
]