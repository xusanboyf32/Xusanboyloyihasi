from django.db.models import QuerySet, Count, Prefetch

from .models import Quiz, Question, Answer, QuizAttempt


def get_quiz_by_id(quiz_id: int) -> Quiz | None:
    """ID bo'yicha quiz olish"""
    try:
        return Quiz.objects.select_related('lesson').get(id=quiz_id)
    except Quiz.DoesNotExist:
        return None


def get_quiz_by_lesson(lesson_id: int) -> Quiz | None:
    """Dars bo'yicha quiz olish"""
    try:
        return Quiz.objects.select_related('lesson').get(lesson_id=lesson_id)
    except Quiz.DoesNotExist:
        return None


def get_quiz_with_questions(quiz_id: int) -> Quiz | None:
    """Quiz va savollarini olish"""
    try:
        return Quiz.objects.prefetch_related(
            Prefetch(
                'questions',
                queryset=Question.objects.prefetch_related('answers').order_by('order')
            )
        ).get(id=quiz_id)
    except Quiz.DoesNotExist:
        return None


def get_all_quizzes() -> QuerySet[Quiz]:
    """Barcha quizlar"""
    return Quiz.objects.select_related('lesson').annotate(
        questions_count=Count('questions')
    ).order_by('lesson__order')


def get_quiz_questions(quiz_id: int) -> QuerySet[Question]:
    """Quiz savollari"""
    return Question.objects.filter(
        quiz_id=quiz_id
    ).prefetch_related('answers').order_by('order')


def get_question_by_id(question_id: int) -> Question | None:
    """ID bo'yicha savol olish"""
    try:
        return Question.objects.prefetch_related('answers').get(id=question_id)
    except Question.DoesNotExist:
        return None


def get_user_quiz_attempts(user_id: int, quiz_id: int) -> QuerySet[QuizAttempt]:
    """Foydalanuvchining quiz urinishlari"""
    return QuizAttempt.objects.filter(
        user_id=user_id,
        quiz_id=quiz_id
    ).order_by('-created_at')


def get_user_attempt_count(user_id: int, quiz_id: int) -> int:
    """Foydalanuvchining urinishlar soni"""
    return QuizAttempt.objects.filter(
        user_id=user_id,
        quiz_id=quiz_id
    ).count()


def has_user_passed_quiz(user_id: int, quiz_id: int) -> bool:
    """Foydalanuvchi testdan o'tganmi?"""
    return QuizAttempt.objects.filter(
        user_id=user_id,
        quiz_id=quiz_id,
        is_passed=True
    ).exists()


def get_best_attempt(user_id: int, quiz_id: int) -> QuizAttempt | None:
    """Foydalanuvchining eng yaxshi urinishi"""
    return QuizAttempt.objects.filter(
        user_id=user_id,
        quiz_id=quiz_id
    ).order_by('-score').first()


def can_user_attempt_quiz(user_id: int, quiz_id: int) -> tuple[bool, str]:
    """
    Foydalanuvchi quiz yecha oladimi?
    Returns: (can_attempt, reason)
    """
    quiz = get_quiz_by_id(quiz_id)

    if not quiz:
        return False, "Test topilmadi"

    if not quiz.is_active:
        return False, "Test hozirda faol emas"

    # Allaqachon o'tganmi?
    if has_user_passed_quiz(user_id, quiz_id):
        return False, "Siz bu testdan allaqachon o'tgansiz"

    # Urinishlar soni
    attempts_count = get_user_attempt_count(user_id, quiz_id)
    if attempts_count >= quiz.max_attempts:
        return False, f"Maksimal urinishlar soni ({quiz.max_attempts}) tugadi"

    return True, ""