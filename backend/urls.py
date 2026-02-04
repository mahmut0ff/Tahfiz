from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/', include('apps.user.urls')),
    path('student/', include('apps.student.urls')),
    path('teacher/', include('apps.teacher.urls')),
    path('group/', include('apps.group.urls')),
    path('schedule/', include('apps.schedule.urls')),
    path('administrator/', include('apps.administrator.urls')),
    path('grade/', include('apps.grade.urls')),
    path('graduate/', include('apps.graduate.urls')),
    path('', include('apps.dashboard.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)