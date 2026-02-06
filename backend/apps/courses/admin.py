from django.contrib import admin

from .models import Lesson, LessonSchedule


class LessonScheduleInline(admin.TabularInline):
    model = LessonSchedule
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'video_duration', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [LessonScheduleInline]


@admin.register(LessonSchedule)
class LessonScheduleAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'group_type', 'available_from')
    list_filter = ('group_type',)