from django.contrib import admin

from .models import UserProgress


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'progress_percent', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'lesson')
    search_fields = ('user__full_name', 'user__phone_number')