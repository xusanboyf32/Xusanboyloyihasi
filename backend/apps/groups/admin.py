from django.contrib import admin

from .models import GroupType, Group


@admin.register(GroupType)
class GroupTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_type', 'students_count', 'is_active', 'created_at')
    list_filter = ('group_type', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}