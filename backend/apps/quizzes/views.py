from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Quiz, QuizAttempt
from .selectors import (
    get_quiz_by_id,
    get_quiz_with_questions,
    get_user_quiz_attempts,
    can_user_attempt_quiz,
    get_user_attempt_count,
    has_user_passed_quiz,
    get_best_attempt
)
from .services import submit_quiz_attempt


class StudentRequiredMixin(LoginRequiredMixin):
    """O'quvchi ekanligini tekshirish"""
    login_url = 'accounts:login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_student:
            messages.error(request, "Faqat o'quvchilar uchun")
            return redirect('accounts:login')
        return super().dispatch(request, *args, **kwargs)


class QuizDetailView(StudentRequiredMixin, View):
    """Quiz haqida ma'lumot"""
    template_name = 'student/quizzes/detail.html'

    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz.objects.select_related('lesson'), id=quiz_id)

        # User urinishlari
        attempts = get_user_quiz_attempts(request.user.id, quiz_id)
        attempts_count = attempts.count()
        best_attempt = get_best_attempt(request.user.id, quiz_id)
        has_passed = has_user_passed_quiz(request.user.id, quiz_id)

        # Test boshlash mumkinmi
        can_attempt, reason = can_user_attempt_quiz(request.user.id, quiz_id)

        context = {
            'quiz': quiz,
            'attempts': attempts,
            'attempts_count': attempts_count,
            'best_attempt': best_attempt,
            'has_passed': has_passed,
            'can_attempt': can_attempt,
            'attempt_reason': reason,
            'remaining_attempts': quiz.max_attempts - attempts_count
        }

        return render(request, self.template_name, context)


class QuizStartView(StudentRequiredMixin, View):
    """Testni boshlash"""
    template_name = 'student/quizzes/start.html'

    def get(self, request, quiz_id):
        quiz = get_quiz_with_questions(quiz_id)

        if not quiz:
            messages.error(request, "Test topilmadi")
            return redirect('student:dashboard')

        # Tekshirish
        can_attempt, reason = can_user_attempt_quiz(request.user.id, quiz_id)

        if not can_attempt:
            messages.error(request, reason)
            return redirect('quizzes:detail', quiz_id=quiz_id)

        attempts_count = get_user_attempt_count(request.user.id, quiz_id)

        context = {
            'quiz': quiz,
            'questions': quiz.questions.all(),
            'attempt_number': attempts_count + 1
        }

        return render(request, self.template_name, context)


class QuizSubmitView(StudentRequiredMixin, View):
    """Javoblarni topshirish"""

    def post(self, request, quiz_id):
        quiz = get_quiz_by_id(quiz_id)

        if not quiz:
            messages.error(request, "Test topilmadi")
            return redirect('student:dashboard')

        # Tekshirish
        can_attempt, reason = can_user_attempt_quiz(request.user.id, quiz_id)

        if not can_attempt:
            messages.error(request, reason)
            return redirect('quizzes:detail', quiz_id=quiz_id)

        # Javoblarni olish
        answers = {}
        for key, value in request.POST.items():
            if key.startswith('question_'):
                question_id = int(key.replace('question_', ''))
                answers[question_id] = int(value)

        if not answers:
            messages.error(request, "Kamida bitta savolga javob bering")
            return redirect('quizzes:start', quiz_id=quiz_id)

        # Topshirish
        attempt = submit_quiz_attempt(
            user_id=request.user.id,
            quiz_id=quiz_id,
            answers=answers
        )

        return redirect('quizzes:result', quiz_id=quiz_id, attempt_id=attempt.id)


class QuizResultView(StudentRequiredMixin, View):
    """Test natijasi"""
    template_name = 'student/quizzes/result.html'

    def get(self, request, quiz_id, attempt_id):
        quiz = get_object_or_404(Quiz.objects.select_related('lesson'), id=quiz_id)
        attempt = get_object_or_404(
            QuizAttempt.objects.filter(user=request.user),
            id=attempt_id,
            quiz_id=quiz_id
        )

        # Keyingi darsga o'tish mumkinmi
        can_proceed = attempt.is_passed

        # SVG uchun stroke-dasharray hisoblash
        stroke_dasharray = attempt.score * 4.4

        context = {
            'quiz': quiz,
            'attempt': attempt,
            'can_proceed': can_proceed,
            'remaining_attempts': quiz.max_attempts - get_user_attempt_count(request.user.id, quiz_id),
            'stroke_dasharray': stroke_dasharray
        }

        return render(request, self.template_name, context)

