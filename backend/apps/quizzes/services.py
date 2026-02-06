from django.db import transaction

from .models import Quiz, Question, Answer, QuizAttempt
from .selectors import get_quiz_by_id, get_quiz_questions


def create_quiz(
        lesson_id: int,
        title: str,
        passing_score: int = 70,
        max_attempts: int = 3
) -> Quiz:
    """Yangi quiz yaratish"""
    return Quiz.objects.create(
        lesson_id=lesson_id,
        title=title,
        passing_score=passing_score,
        max_attempts=max_attempts
    )


def update_quiz(quiz_id: int, **kwargs) -> Quiz | None:
    """Quiz yangilash"""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return None

    allowed_fields = ['title', 'passing_score', 'max_attempts', 'is_active']

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(quiz, field, value)

    quiz.save()
    return quiz


def delete_quiz(quiz_id: int) -> bool:
    """Quiz o'chirish"""
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        return False

    quiz.delete()
    return True


def create_question(
        quiz_id: int,
        text: str,
        order: int = 0
) -> Question:
    """Yangi savol yaratish"""
    return Question.objects.create(
        quiz_id=quiz_id,
        text=text,
        order=order
    )


def update_question(question_id: int, **kwargs) -> Question | None:
    """Savolni yangilash"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return None

    allowed_fields = ['text', 'order']

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(question, field, value)

    question.save()
    return question


def delete_question(question_id: int) -> bool:
    """Savolni o'chirish"""
    try:
        question = Question.objects.get(id=question_id)
        question.delete()
        return True
    except Question.DoesNotExist:
        return False


def create_answer(
        question_id: int,
        text: str,
        is_correct: bool = False
) -> Answer:
    """Yangi javob yaratish"""
    return Answer.objects.create(
        question_id=question_id,
        text=text,
        is_correct=is_correct
    )


def update_answer(answer_id: int, **kwargs) -> Answer | None:
    """Javobni yangilash"""
    try:
        answer = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return None

    allowed_fields = ['text', 'is_correct']

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(answer, field, value)

    answer.save()
    return answer


def delete_answer(answer_id: int) -> bool:
    """Javobni o'chirish"""
    try:
        answer = Answer.objects.get(id=answer_id)
        answer.delete()
        return True
    except Answer.DoesNotExist:
        return False


def set_correct_answer(question_id: int, answer_id: int) -> bool:
    """To'g'ri javobni belgilash"""
    try:
        # Barcha javoblarni noto'g'ri qilish
        Answer.objects.filter(question_id=question_id).update(is_correct=False)
        # Tanlangan javobni to'g'ri qilish
        Answer.objects.filter(id=answer_id, question_id=question_id).update(is_correct=True)
        return True
    except Exception:
        return False


@transaction.atomic
def submit_quiz_attempt(
        user_id: int,
        quiz_id: int,
        answers: dict[int, int]  # {question_id: answer_id}
) -> QuizAttempt:
    """
    Quiz javoblarini topshirish

    Args:
        user_id: Foydalanuvchi ID
        quiz_id: Quiz ID
        answers: {question_id: answer_id} formatda javoblar

    Returns:
        QuizAttempt object
    """
    quiz = get_quiz_by_id(quiz_id)
    questions = get_quiz_questions(quiz_id)

    total_questions = questions.count()
    correct_count = 0

    # Javoblarni tekshirish
    for question in questions:
        selected_answer_id = answers.get(question.id)
        if selected_answer_id:
            # To'g'ri javobni tekshirish
            correct_answer = question.answers.filter(is_correct=True).first()
            if correct_answer and correct_answer.id == selected_answer_id:
                correct_count += 1

    # Ball hisoblash
    score = int((correct_count / total_questions) * 100) if total_questions > 0 else 0
    is_passed = score >= quiz.passing_score

    # Urinishni saqlash
    attempt = QuizAttempt.objects.create(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score,
        is_passed=is_passed
    )

    return attempt


def create_question_with_answers(
        quiz_id: int,
        text: str,
        answers_data: list[dict],  # [{'text': str, 'is_correct': bool}, ...]
        order: int = 0
) -> Question:
    """Savol va javoblarini birga yaratish"""
    with transaction.atomic():
        question = create_question(quiz_id, text, order)

        for answer_data in answers_data:
            create_answer(
                question_id=question.id,
                text=answer_data.get('text', ''),
                is_correct=answer_data.get('is_correct', False)
            )

        return question