from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    # Asosiy
    path('', views.DashboardIndexView.as_view(), name='index'),

    # Guruh turlari
    path('group-types/', views.GroupTypeListView.as_view(), name='group_type_list'),
    path('group-types/create/', views.GroupTypeCreateView.as_view(), name='group_type_create'),
    path('group-types/<int:pk>/', views.GroupTypeDetailView.as_view(), name='group_type_detail'),
    path('group-types/<int:pk>/edit/', views.GroupTypeEditView.as_view(), name='group_type_edit'),
    path('group-types/<int:pk>/delete/', views.GroupTypeDeleteView.as_view(), name='group_type_delete'),

    # Guruhlar
    path('groups/', views.GroupListView.as_view(), name='group_list'),
    path('groups/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('groups/<int:pk>/edit/', views.GroupEditView.as_view(), name='group_edit'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView.as_view(), name='group_delete'),

    # O'quvchilar
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/create/', views.StudentCreateView.as_view(), name='student_create'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', views.StudentEditView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),

    # Darslar
    path('lessons/', views.LessonListView.as_view(), name='lesson_list'),
    path('lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('lessons/<int:pk>/edit/', views.LessonEditView.as_view(), name='lesson_edit'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson_delete'),

    # Testlar
    path('quizzes/', views.QuizListView.as_view(), name='quiz_list'),
    path('quizzes/create/', views.QuizCreateView.as_view(), name='quiz_create'),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz_detail'),
    path('quizzes/<int:pk>/edit/', views.QuizEditView.as_view(), name='quiz_edit'),
    path('quizzes/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz_delete'),

    # Savollar
    path('quizzes/<int:quiz_pk>/questions/create/', views.QuestionCreateView.as_view(), name='question_create'),
    path('quizzes/<int:quiz_pk>/questions/<int:question_pk>/edit/', views.QuestionEditView.as_view(),
         name='question_edit'),
    path('quizzes/<int:quiz_pk>/questions/<int:question_pk>/delete/', views.QuestionDeleteView.as_view(),
         name='question_delete'),

    # Adminlar
    path('admins/', views.AdminListView.as_view(), name='admin_list'),
    path('admins/create/', views.AdminCreateView.as_view(), name='admin_create'),
    path('admins/<int:pk>/delete/', views.AdminDeleteView.as_view(), name='admin_delete'),
]