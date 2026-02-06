from django.urls import path

from . import views

app_name = 'student'

urlpatterns = [
    path('', views.StudentDashboardView.as_view(), name='dashboard'),
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('lessons/<slug:slug>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<slug:slug>/complete/', views.MarkLessonCompleteView.as_view(), name='lesson_complete'),
    path('lessons/<slug:slug>/progress/', views.UpdateProgressView.as_view(), name='update_progress'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]