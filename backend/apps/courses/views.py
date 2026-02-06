import json

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .models import Lesson
from .selectors import (
    get_all_lessons,
    get_lesson_by_slug,
    get_available_lessons_for_group_type,
    is_lesson_available_for_user
)
from apps.progress.selectors import (
    get_user_progress,
    get_all_user_progress,
    get_user_current_lesson,
    can_user_access_lesson
)
from apps.progress.services import update_video_progress, mark_lesson_completed



class StudentRequiredMixin(LoginRequiredMixin):
    """O'quvchi bo'lishi shart"""
    login_url = 'accounts:login'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')

        # Admin bo'lsa dashboard ga yo'naltirish
        if request.user.is_admin:
            return redirect('dashboard:index')

        return super().dispatch(request, *args, **kwargs)


class StudentDashboardView(StudentRequiredMixin, View):
    """O'quvchi bosh sahifasi"""
    template_name = 'student/dashboard.html'

    def get(self, request):
        user = request.user

        # Agar guruhga biriktirilmagan bo'lsa
        if not user.group:
            return render(request, 'student/no_group.html')

        # Foydalanuvchi uchun ochiq darslar
        available_lessons = get_available_lessons_for_group_type(user.group.group_type_id)

        # Progress
        all_progress = get_all_user_progress(user.id)
        current_lesson_number = get_user_current_lesson(user.id)

        # Completed lessons count
        completed_count = all_progress.filter(is_completed=True).count()
        total_lessons = available_lessons.count()

        # Progress percentage
        progress_percent = int((completed_count / total_lessons * 100)) if total_lessons > 0 else 0

        # Joriy dars
        current_lesson = available_lessons.filter(order=current_lesson_number).first()
        if not current_lesson:
            current_lesson = available_lessons.first()

        context = {
            'current_lesson': current_lesson,
            'current_lesson_number': current_lesson_number,
            'completed_count': completed_count,
            'total_lessons': total_lessons,
            'progress_percent': progress_percent,
            'recent_lessons': available_lessons[:5],
        }

        return render(request, self.template_name, context)


class LessonListView(StudentRequiredMixin, View):
    """Barcha darslar ro'yxati"""
    template_name = 'student/lessons/list.html'

    def get(self, request):
        user = request.user

        if not user.group:
            return render(request, 'student/no_group.html')

        available_lessons = get_available_lessons_for_group_type(user.group.group_type_id)
        all_progress = {p.lesson_id: p for p in get_all_user_progress(user.id)}
        current_lesson_number = get_user_current_lesson(user.id)

        # Darslarni progress bilan birlashtirish
        lessons_with_progress = []
        for lesson in available_lessons:
            progress = all_progress.get(lesson.id)
            can_access = can_user_access_lesson(user, lesson)

            lessons_with_progress.append({
                'lesson': lesson,
                'progress': progress,
                'can_access': can_access,
                'is_current': lesson.order == current_lesson_number,
            })

        return render(request, self.template_name, {
            'lessons': lessons_with_progress,
            'current_lesson_number': current_lesson_number,
        })


class LessonDetailView(StudentRequiredMixin, View):
    """Dars tafsilotlari - video ko'rish"""
    template_name = 'student/lessons/detail.html'

    def get(self, request, slug):
        user = request.user

        if not user.group:
            return render(request, 'student/no_group.html')

        lesson = get_object_or_404(Lesson, slug=slug, is_active=True)

        # Darsga kirish huquqini tekshirish
        if not can_user_access_lesson(user, lesson):
            messages.error(request, "Bu darsga hali kirishingiz mumkin emas. Oldingi darsni yakunlang.")
            return redirect('student:lesson_list')

        # Progress
        progress = get_user_progress(user.id, lesson.id)

        # Oldingi va keyingi darslar
        prev_lesson = Lesson.objects.filter(order__lt=lesson.order, is_active=True).order_by('-order').first()
        next_lesson = Lesson.objects.filter(order__gt=lesson.order, is_active=True).order_by('order').first()

        # Keyingi darsga kirish mumkinmi
        can_access_next = False
        if next_lesson and progress and progress.is_completed:
            can_access_next = can_user_access_lesson(user, next_lesson)

        # Notion content olish
        notion_content = ""
        if lesson.notion_page_id:
            try:
                from integrations.notion import get_lesson_content
                notion_content = get_lesson_content(lesson)
            except Exception as e:
                print(f"Notion content error: {e}")

        # Kinescope secure URL
        kinescope_embed_url = ""
        if lesson.kinescope_video_id:
            try:
                from integrations.kinescope import get_secure_embed_url
                kinescope_embed_url = get_secure_embed_url(lesson.kinescope_video_id, user.id)
            except Exception:
                kinescope_embed_url = f"https://kinescope.io/embed/{lesson.kinescope_video_id}"

        context = {
            'lesson': lesson,
            'progress': progress,
            'prev_lesson': prev_lesson,
            'next_lesson': next_lesson,
            'can_access_next': can_access_next,
            'notion_content': notion_content,
            'kinescope_embed_url': kinescope_embed_url,
        }

        return render(request, self.template_name, context)


class MarkLessonCompleteView(StudentRequiredMixin, View):
    """Darsni tugatilgan deb belgilash"""

    def post(self, request, slug):
        user = request.user
        lesson = get_object_or_404(Lesson, slug=slug, is_active=True)

        if not can_user_access_lesson(user, lesson):
            messages.error(request, "Bu darsga kirishingiz mumkin emas")
            return redirect('student:lesson_list')

        mark_lesson_completed(user.id, lesson.id)
        messages.success(request, f"'{lesson.title}' darsi yakunlandi!")

        # Keyingi darsga o'tish
        next_lesson = Lesson.objects.filter(order__gt=lesson.order, is_active=True).order_by('order').first()
        if next_lesson and can_user_access_lesson(user, next_lesson):
            return redirect('student:lesson_detail', slug=next_lesson.slug)

        return redirect('student:lesson_list')


@method_decorator(csrf_exempt, name='dispatch')
class UpdateProgressView(StudentRequiredMixin, View):
    """Video progress yangilash (AJAX)"""

    def post(self, request, slug):
        try:
            user = request.user
            lesson = get_object_or_404(Lesson, slug=slug, is_active=True)

            data = json.loads(request.body)
            progress_seconds = int(data.get('progress', 0))

            update_video_progress(user.id, lesson.id, progress_seconds)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class ProfileView(StudentRequiredMixin, View):
    """O'quvchi profili"""
    template_name = 'student/profile.html'

    def get(self, request):
        user = request.user
        all_progress = get_all_user_progress(user.id)
        current_lesson = get_user_current_lesson(user.id)

        completed_count = all_progress.filter(is_completed=True).count()

        return render(request, self.template_name, {
            'user': user,
            'progress': all_progress,
            'current_lesson': current_lesson,
            'completed_count': completed_count,
        })