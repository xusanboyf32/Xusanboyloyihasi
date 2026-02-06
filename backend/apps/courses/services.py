from django.utils.text import slugify
from datetime import datetime

from .models import Lesson, LessonSchedule
from .selectors import get_lesson_by_id


def create_lesson(
        title: str,
        description: str = '',
        order: int = 0,
        kinescope_video_id: str = '',
        notion_page_id: str = ''
) -> Lesson:
    """Yangi dars yaratish"""
    return Lesson.objects.create(
        title=title,
        description=description,
        order=order,
        kinescope_video_id=kinescope_video_id,
        notion_page_id=notion_page_id,
        slug=slugify(f"{order}-{title}")
    )


def update_lesson(lesson_id: int, **kwargs) -> Lesson | None:
    """Darsni yangilash"""
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        return None

    allowed_fields = [
        'title', 'description', 'order',
        'kinescope_video_id', 'notion_page_id',
        'video_duration', 'is_active'
    ]

    for field, value in kwargs.items():
        if field in allowed_fields:
            setattr(lesson, field, value)

    lesson.save()
    return lesson


def delete_lesson(lesson_id: int) -> bool:
    """Darsni o'chirish (soft delete)"""
    lesson = get_lesson_by_id(lesson_id)
    if not lesson:
        return False

    lesson.is_active = False
    lesson.save(update_fields=['is_active', 'updated_at'])
    return True


def schedule_lesson_for_group_type(
        lesson_id: int,
        group_type_id: int,
        available_from: datetime
) -> LessonSchedule:
    """Darsni guruh turi uchun jadvalga qo'yish"""
    schedule, created = LessonSchedule.objects.update_or_create(
        lesson_id=lesson_id,
        group_type_id=group_type_id,
        defaults={'available_from': available_from}
    )
    return schedule


def remove_lesson_schedule(lesson_id: int, group_type_id: int) -> bool:
    """Dars jadvalini o'chirish"""
    deleted, _ = LessonSchedule.objects.filter(
        lesson_id=lesson_id,
        group_type_id=group_type_id
    ).delete()
    return deleted > 0


