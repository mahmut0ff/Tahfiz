from django.urls import path
from .views import *

app_name = 'teacher'

urlpatterns = [
    path('', list, name='list'),
    path('create/', create, name='create'),
    path('<int:pk>/', details, name='details'),
    path('<int:pk>/delete/', delete, name='delete'),
    path('students/', students, name='students'),
    path('reports/', report_list, name='reports'),
    path('code/', code, name='code'),
    path('code/generated/', generated_code, name='generated_code'),
    path('attendance/', attendance_list, name='attendance'),
]