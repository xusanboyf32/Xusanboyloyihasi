from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('auth/', include('apps.accounts.urls', namespace='accounts')),

    # Dashboard (admin panel)
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),

    # Quizzes (student)
    path('quizzes/', include('apps.quizzes.urls', namespace='quizzes')),

    # Student panel
    path('', include('apps.courses.urls', namespace='student')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    try:
        import debug_toolbar

        urlpatterns = [
                          path('__debug__/', include(debug_toolbar.urls)),
                      ] + urlpatterns
    except ImportError:
        pass

