from django.db import models
from django.utils.text import slugify

from core.mixins import TimeStampMixin, SlugMixin


class Lesson(TimeStampMixin, SlugMixin):
    """Video dars"""

    title = models.CharField(
        max_length=255,
        verbose_name="Sarlavha"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Tavsif"
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Tartib raqami"
    )

    # Kinescope integration
    kinescope_video_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Kinescope Video ID"
    )
    video_duration = models.PositiveIntegerField(
        default=0,
        help_text="Davomiyligi sekundlarda",
        verbose_name="Video davomiyligi"
    )

    # Notion integration
    notion_page_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Notion Page ID"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    class Meta:
        verbose_name = "Dars"
        verbose_name_plural = "Darslar"
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.order}-{self.title}")
        super().save(*args, **kwargs)


class LessonSchedule(TimeStampMixin):
    """
    Darsning qaysi guruh turiga qachon ochilishini belgilash
    """
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name="Dars"
    )
    group_type = models.ForeignKey(
        'groups.GroupType',
        on_delete=models.CASCADE,
        related_name='lesson_schedules',
        verbose_name="Guruh turi"
    )
    available_from = models.DateTimeField(
        verbose_name="Ochilish vaqti"
    )

    class Meta:
        verbose_name = "Dars jadvali"
        verbose_name_plural = "Dars jadvallari"
        unique_together = ['lesson', 'group_type']
        ordering = ['available_from']

    def __str__(self):
        return f"{self.lesson.title} - {self.group_type.name}"

