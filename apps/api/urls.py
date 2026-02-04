from django.urls import path
from .views import *

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('student/', StudentRetrieveView.as_view(), name='student-retrieve-api'),
    path('group/<int:pk>/', GroupRetrieveView.as_view(), name='group-retrieve-api'),
    path('groups/', GroupListView.as_view(), name='group-list-api'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('diary/', DiaryAPIView.as_view(), name='diary-api'),
]