from django.db import models
from django.utils.text import slugify

from core.mixins import TimeStampMixin, SlugMixin


class GroupType(TimeStampMixin, SlugMixin):
    """
    Guruh tipi - masalan: 7.0 A, 7.0 B, Premium
    Har bir tipdagi guruhlar bir xil darslarni ko'radi
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nomi"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Tavsif"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    class Meta:
        verbose_name = "Guruh turi"
        verbose_name_plural = "Guruh turlari"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Group(TimeStampMixin, SlugMixin):
    """
    Guruh - masalan: B1, B2 (7.0 B tipidagi)
    """
    name = models.CharField(
        max_length=100,
        verbose_name="Nomi"
    )
    group_type = models.ForeignKey(
        GroupType,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name="Guruh turi"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Tavsif"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Faol"
    )

    class Meta:
        verbose_name = "Guruh"
        verbose_name_plural = "Guruhlar"
        ordering = ['group_type', 'name']
        unique_together = ['name', 'group_type']

    def __str__(self):
        return f"{self.group_type.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.group_type.name}-{self.name}")
        super().save(*args, **kwargs)

    @property
    def students_count(self) -> int:
        return self.students.filter(is_active=True).count()
