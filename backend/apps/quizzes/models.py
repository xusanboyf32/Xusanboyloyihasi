from django.db import models
from django.conf import settings

from core.mixins import TimeStampMixin


class Quiz(TimeStampMixin):
    """Dars uchun mini test"""

    lesson = models.OneToOneField(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='quiz',
        verbose_name="Dars"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Sarlavha"
    )
    passing_score = models.PositiveIntegerField(
        default=70,
        help_text="O'tish uchun minimal ball (%)",
        verbose_name="O'tish balli"
    )
    max_attempts = models.PositiveIntegerField(
        default=3,
        verbose_name="Maksimal urinishlar"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    class Meta:
        verbose_name = "Test"
        verbose_name_plural = "Testlar"

    def __str__(self):
        return f"Test: {self.lesson.title}"


class Question(TimeStampMixin):
    """Test savoli"""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Test"
    )
    text = models.TextField(
        verbose_name="Savol matni"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Tartib"
    )

    class Meta:
        verbose_name = "Savol"
        verbose_name_plural = "Savollar"
        ordering = ['order']

    def __str__(self):
        return self.text[:50]


class Answer(TimeStampMixin):
    """Savol javobi"""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Savol"
    )
    text = models.CharField(
        max_length=500,
        verbose_name="Javob matni"
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="To'g'ri javob"
    )

    class Meta:
        verbose_name = "Javob"
        verbose_name_plural = "Javoblar"

    def __str__(self):
        return self.text[:50]


class QuizAttempt(TimeStampMixin):
    """O'quvchining test urinishi"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name="O'quvchi"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Test"
    )
    score = models.PositiveIntegerField(
        default=0,
        verbose_name="Ball"
    )
    is_passed = models.BooleanField(
        default=False,
        verbose_name="O'tdi"
    )

    class Meta:
        verbose_name = "Test urinishi"
        verbose_name_plural = "Test urinishlari"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.full_name} - {self.quiz.title} - {self.score}%"
