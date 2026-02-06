from django.db import models
from django.conf import settings

from core.mixins import TimeStampMixin


class UserProgress(TimeStampMixin):
    """O'quvchining dars progressi"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress',
        verbose_name="O'quvchi"
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='user_progress',
        verbose_name="Dars"
    )
    video_progress = models.PositiveIntegerField(
        default=0,
        help_text="Video ko'rilgan qismi (sekundlarda)",
        verbose_name="Video progress"
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="Tugatilgan"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Tugatilgan vaqt"
    )

    class Meta:
        verbose_name = "O'quvchi progressi"
        verbose_name_plural = "O'quvchilar progressi"
        unique_together = ['user', 'lesson']

    def __str__(self):
        return f"{self.user.full_name} - {self.lesson.title}"

    @property
    def progress_percent(self) -> int:
        """Video progress foizda"""
        if self.lesson.video_duration == 0:
            return 0
        return min(100, int(self.video_progress / self.lesson.video_duration * 100))

