from django.urls import path

from . import views

app_name = 'quizzes'

urlpatterns = [
    # Student quiz views
    path('<int:quiz_id>/', views.QuizDetailView.as_view(), name='detail'),
    path('<int:quiz_id>/start/', views.QuizStartView.as_view(), name='start'),
    path('<int:quiz_id>/submit/', views.QuizSubmitView.as_view(), name='submit'),
    path('<int:quiz_id>/result/<int:attempt_id>/', views.QuizResultView.as_view(), name='result'),
]
