from django.contrib.auth import views as auth_views
from django.urls import path
from .views  import *

app_name = 'user'

urlpatterns = [
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('update/', update, name='update'),
]