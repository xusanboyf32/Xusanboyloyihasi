from django.db import models


class TimeStampMixin(models.Model):
    """Barcha modellar uchun vaqt maydonlari"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # abstract bunda models.model deyilsa ham jadval yaratilmedi, chunki """abstract true""" meros oladi


class SlugMixin(models.Model):
    """Slug kerak bo'lgan modellar uchun"""
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        abstract = True

