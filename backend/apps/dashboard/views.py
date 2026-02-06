from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.db.models import Count, Q

from .permissions import AdminRequiredMixin, SuperAdminRequiredMixin

from apps.accounts.models import User
from apps.accounts.services import create_student, create_admin, update_user
from apps.accounts.selectors import get_user_by_id, get_students_by_group, get_all_admins

from apps.groups.models import GroupType, Group
from apps.groups.services import (
    create_group_type, update_group_type, delete_group_type,
    create_group, update_group, delete_group
)
from apps.groups.selectors import (
    get_all_group_types, get_group_type_by_id,
    get_all_groups, get_groups_by_type, get_group_by_id
)

from apps.courses.models import Lesson
from apps.courses.services import create_lesson, update_lesson, delete_lesson
from apps.courses.selectors import get_all_lessons, get_lesson_by_id

from apps.progress.selectors import get_user_current_lesson


# ============== DASHBOARD INDEX ==============

class DashboardIndexView(AdminRequiredMixin, View):
    """Asosiy dashboard - statistika"""
    template_name = 'admin_panel/dashboard.html'

    def get(self, request):
        context = {
            'total_students': User.objects.filter(role=User.Role.STUDENT, is_active=True).count(),
            'total_groups': Group.objects.filter(is_active=True).count(),
            'total_lessons': Lesson.objects.filter(is_active=True).count(),
            'total_group_types': GroupType.objects.filter(is_active=True).count(),

            # Oxirgi qo'shilgan o'quvchilar
            'recent_students': User.objects.filter(
                role=User.Role.STUDENT
            ).select_related('group').order_by('-created_at')[:5],

            # Guruhlar statistikasi
            'groups_stats': Group.objects.filter(
                is_active=True
            ).annotate(
                student_count=Count('students', filter=Q(students__is_active=True))
            ).select_related('group_type')[:10],
        }
        return render(request, self.template_name, context)


# ============== GROUP TYPES ==============

class GroupTypeListView(AdminRequiredMixin, View):
    """Guruh turlari ro'yxati"""
    template_name = 'admin_panel/group_types/list.html'

    def get(self, request):
        group_types = GroupType.objects.annotate(
            groups_count=Count('groups', filter=Q(groups__is_active=True))
        ).order_by('name')

        return render(request, self.template_name, {'group_types': group_types})


class GroupTypeCreateView(AdminRequiredMixin, View):
    """Yangi guruh turi yaratish"""
    template_name = 'admin_panel/group_types/form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, "Nomni kiriting")
            return render(request, self.template_name)

        if GroupType.objects.filter(name=name).exists():
            messages.error(request, "Bu nomdagi tur mavjud")
            return render(request, self.template_name)

        create_group_type(name=name, description=description)
        messages.success(request, f"'{name}' turi yaratildi")
        return redirect('dashboard:group_type_list')


class GroupTypeDetailView(AdminRequiredMixin, View):
    """Guruh turi tafsilotlari"""
    template_name = 'admin_panel/group_types/detail.html'

    def get(self, request, pk):
        group_type = get_object_or_404(GroupType, pk=pk)
        groups = get_groups_by_type(group_type.id)

        return render(request, self.template_name, {
            'group_type': group_type,
            'groups': groups
        })


class GroupTypeEditView(AdminRequiredMixin, View):
    """Guruh turini tahrirlash"""
    template_name = 'admin_panel/group_types/form.html'

    def get(self, request, pk):
        group_type = get_object_or_404(GroupType, pk=pk)
        return render(request, self.template_name, {'group_type': group_type})

    def post(self, request, pk):
        group_type = get_object_or_404(GroupType, pk=pk)

        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, "Nomni kiriting")
            return render(request, self.template_name, {'group_type': group_type})

        update_group_type(pk, name=name, description=description)
        messages.success(request, "O'zgarishlar saqlandi")
        return redirect('dashboard:group_type_list')


class GroupTypeDeleteView(AdminRequiredMixin, View):
    """Guruh turini o'chirish"""

    def post(self, request, pk):
        group_type = get_object_or_404(GroupType, pk=pk)
        delete_group_type(pk)
        messages.success(request, f"'{group_type.name}' o'chirildi")
        return redirect('dashboard:group_type_list')


# ============== GROUPS ==============

class GroupListView(AdminRequiredMixin, View):
    """Guruhlar ro'yxati"""
    template_name = 'admin_panel/groups/list.html'

    def get(self, request):
        groups = Group.objects.filter(
            is_active=True
        ).annotate(
            student_count=Count('students', filter=Q(students__is_active=True))
        ).select_related('group_type').order_by('group_type__name', 'name')

        group_types = get_all_group_types()

        # Filtrlash
        type_filter = request.GET.get('type')
        if type_filter:
            groups = groups.filter(group_type_id=type_filter)

        return render(request, self.template_name, {
            'groups': groups,
            'group_types': group_types,
            'selected_type': type_filter
        })


class GroupCreateView(AdminRequiredMixin, View):
    """Yangi guruh yaratish"""
    template_name = 'admin_panel/groups/form.html'

    def get(self, request):
        group_types = get_all_group_types()
        return render(request, self.template_name, {'group_types': group_types})

    def post(self, request):
        name = request.POST.get('name', '').strip()
        group_type_id = request.POST.get('group_type_id')
        description = request.POST.get('description', '').strip()

        group_types = get_all_group_types()

        if not name or not group_type_id:
            messages.error(request, "Barcha maydonlarni to'ldiring")
            return render(request, self.template_name, {'group_types': group_types})

        create_group(name=name, group_type_id=int(group_type_id), description=description)
        messages.success(request, f"'{name}' guruhi yaratildi")
        return redirect('dashboard:group_list')


class GroupDetailView(AdminRequiredMixin, View):
    """Guruh tafsilotlari - o'quvchilar ro'yxati"""
    template_name = 'admin_panel/groups/detail.html'

    def get(self, request, pk):
        group = get_object_or_404(Group.objects.select_related('group_type'), pk=pk)
        students = get_students_by_group(pk)

        # Har bir o'quvchi uchun qaysi darsda ekanligini olish
        students_with_progress = []
        for student in students:
            current_lesson = get_user_current_lesson(student.id)
            students_with_progress.append({
                'student': student,
                'current_lesson': current_lesson
            })

        return render(request, self.template_name, {
            'group': group,
            'students_with_progress': students_with_progress
        })


class GroupEditView(AdminRequiredMixin, View):
    """Guruhni tahrirlash"""
    template_name = 'admin_panel/groups/form.html'

    def get(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        group_types = get_all_group_types()
        return render(request, self.template_name, {
            'group': group,
            'group_types': group_types
        })

    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)

        name = request.POST.get('name', '').strip()
        group_type_id = request.POST.get('group_type_id')
        description = request.POST.get('description', '').strip()

        if not name or not group_type_id:
            messages.error(request, "Barcha maydonlarni to'ldiring")
            group_types = get_all_group_types()
            return render(request, self.template_name, {
                'group': group,
                'group_types': group_types
            })

        update_group(pk, name=name, group_type_id=int(group_type_id), description=description)
        messages.success(request, "O'zgarishlar saqlandi")
        return redirect('dashboard:group_list')


class GroupDeleteView(AdminRequiredMixin, View):
    """Guruhni o'chirish"""

    def post(self, request, pk):
        group = get_object_or_404(Group, pk=pk)
        delete_group(pk)
        messages.success(request, f"'{group.name}' o'chirildi")
        return redirect('dashboard:group_list')


# ============== STUDENTS ==============

class StudentListView(AdminRequiredMixin, View):
    """O'quvchilar ro'yxati"""
    template_name = 'admin_panel/students/list.html'

    def get(self, request):
        students = User.objects.filter(
            role=User.Role.STUDENT
        ).select_related('group', 'group__group_type').order_by('-created_at')

        groups = get_all_groups()

        # Filtrlash
        group_filter = request.GET.get('group')
        search = request.GET.get('search', '').strip()

        if group_filter:
            students = students.filter(group_id=group_filter)

        if search:
            students = students.filter(
                Q(full_name__icontains=search) | Q(phone_number__icontains=search)
            )

        return render(request, self.template_name, {
            'students': students,
            'groups': groups,
            'selected_group': group_filter,
            'search': search
        })


class StudentCreateView(AdminRequiredMixin, View):
    """Yangi o'quvchi qo'shish"""
    template_name = 'admin_panel/students/form.html'

    def get(self, request):
        groups = get_all_groups()
        return render(request, self.template_name, {'groups': groups})

    def post(self, request):
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        group_id = request.POST.get('group_id') or None

        groups = get_all_groups()

        if not full_name or not phone_number:
            messages.error(request, "Ism va telefon raqamni kiriting")
            return render(request, self.template_name, {'groups': groups})

        # Telefon raqamni formatlash
        phone_number = self.format_phone(phone_number)

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Bu raqam allaqachon ro'yxatdan o'tgan")
            return render(request, self.template_name, {'groups': groups})

        create_student(
            phone_number=phone_number,
            full_name=full_name,
            group_id=int(group_id) if group_id else None
        )
        messages.success(request, f"'{full_name}' qo'shildi")
        return redirect('dashboard:student_list')

    def format_phone(self, phone: str) -> str:
        phone = ''.join(filter(str.isdigit, phone))
        if phone.startswith('998') and len(phone) == 12:
            return f"+{phone}"
        elif len(phone) == 9:
            return f"+998{phone}"
        return f"+{phone}" if phone else ''


class StudentDetailView(AdminRequiredMixin, View):
    """O'quvchi tafsilotlari"""
    template_name = 'admin_panel/students/detail.html'

    def get(self, request, pk):
        student = get_object_or_404(
            User.objects.select_related('group', 'group__group_type'),
            pk=pk,
            role=User.Role.STUDENT
        )

        current_lesson = get_user_current_lesson(pk)

        from apps.progress.selectors import get_all_user_progress
        progress = get_all_user_progress(pk)

        return render(request, self.template_name, {
            'student': student,
            'current_lesson': current_lesson,
            'progress': progress
        })


class StudentEditView(AdminRequiredMixin, View):
    """O'quvchini tahrirlash"""
    template_name = 'admin_panel/students/form.html'

    def get(self, request, pk):
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
        groups = get_all_groups()
        return render(request, self.template_name, {
            'student': student,
            'groups': groups
        })

    def post(self, request, pk):
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)

        full_name = request.POST.get('full_name', '').strip()
        phone_number = f"+998{request.POST.get('phone_number', '').strip()}"

        group_id = request.POST.get('group_id') or None

        if not full_name or not phone_number:
            messages.error(request, "Ism va telefon raqamni kiriting")
            groups = get_all_groups()
            return render(request, self.template_name, {
                'student': student,
                'groups': groups
            })

        update_user(
            student,
            full_name=full_name,
            phone_number=phone_number,
            group_id=int(group_id) if group_id else None
        )
        messages.success(request, "O'zgarishlar saqlandi")
        return redirect('dashboard:student_list')


class StudentDeleteView(AdminRequiredMixin, View):
    """O'quvchini o'chirish"""

    def post(self, request, pk):
        student = get_object_or_404(User, pk=pk, role=User.Role.STUDENT)
        student.is_active = False
        student.save()
        messages.success(request, f"'{student.full_name}' o'chirildi")
        return redirect('dashboard:student_list')


# ============== LESSONS ==============

class LessonListView(AdminRequiredMixin, View):
    """Darslar ro'yxati"""
    template_name = 'admin_panel/lessons/list.html'

    def get(self, request):
        lessons = get_all_lessons(only_active=False)
        return render(request, self.template_name, {'lessons': lessons})


class LessonCreateView(AdminRequiredMixin, View):
    """Yangi dars yaratish"""
    template_name = 'admin_panel/lessons/form.html'

    def get(self, request):
        group_types = get_all_group_types()
        return render(request, self.template_name, {'group_types': group_types})

    def post(self, request):
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        order = request.POST.get('order', 0)
        kinescope_video_id = request.POST.get('kinescope_video_id', '').strip()
        notion_page_id = request.POST.get('notion_page_id', '').strip()

        if not title:
            messages.error(request, "Dars nomini kiriting")
            group_types = get_all_group_types()
            return render(request, self.template_name, {'group_types': group_types})

        lesson = create_lesson(
            title=title,
            description=description,
            order=int(order) if order else 0,
            kinescope_video_id=kinescope_video_id,
            notion_page_id=notion_page_id
        )

        messages.success(request, f"'{title}' darsi yaratildi")
        return redirect('dashboard:lesson_detail', pk=lesson.pk)


class LessonDetailView(AdminRequiredMixin, View):
    """Dars tafsilotlari va jadval"""
    template_name = 'admin_panel/lessons/detail.html'

    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        group_types = get_all_group_types()
        schedules = lesson.schedules.select_related('group_type').all()

        return render(request, self.template_name, {
            'lesson': lesson,
            'group_types': group_types,
            'schedules': schedules
        })

    def post(self, request, pk):
        """Jadval qo'shish"""
        lesson = get_object_or_404(Lesson, pk=pk)

        group_type_id = request.POST.get('group_type_id')
        available_from = request.POST.get('available_from')

        if group_type_id and available_from:
            from apps.courses.services import schedule_lesson_for_group_type
            from datetime import datetime

            try:
                # datetime-local formatidan parse qilish
                available_from_dt = datetime.fromisoformat(available_from)
                schedule_lesson_for_group_type(
                    lesson_id=pk,
                    group_type_id=int(group_type_id),
                    available_from=available_from_dt
                )
                messages.success(request, "Jadval qo'shildi")
            except Exception as e:
                messages.error(request, f"Xatolik: {str(e)}")
        else:
            messages.error(request, "Barcha maydonlarni to'ldiring")

        return redirect('dashboard:lesson_detail', pk=pk)


class LessonEditView(AdminRequiredMixin, View):
    """Darsni tahrirlash"""
    template_name = 'admin_panel/lessons/form.html'

    def get(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        group_types = get_all_group_types()
        return render(request, self.template_name, {
            'lesson': lesson,
            'group_types': group_types
        })

    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        order = request.POST.get('order', 0)
        kinescope_video_id = request.POST.get('kinescope_video_id', '').strip()
        notion_page_id = request.POST.get('notion_page_id', '').strip()
        is_active = request.POST.get('is_active') == 'on'

        if not title:
            messages.error(request, "Dars nomini kiriting")
            group_types = get_all_group_types()
            return render(request, self.template_name, {
                'lesson': lesson,
                'group_types': group_types
            })

        update_lesson(
            pk,
            title=title,
            description=description,
            order=int(order) if order else 0,
            kinescope_video_id=kinescope_video_id,
            notion_page_id=notion_page_id,
            is_active=is_active
        )

        messages.success(request, "O'zgarishlar saqlandi")
        return redirect('dashboard:lesson_list')


class LessonDeleteView(AdminRequiredMixin, View):
    """Darsni o'chirish"""

    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)
        delete_lesson(pk)
        messages.success(request, f"'{lesson.title}' o'chirildi")
        return redirect('dashboard:lesson_list')


# ============== ADMINS ==============

class AdminListView(SuperAdminRequiredMixin, View):
    """Adminlar ro'yxati (faqat super admin)"""
    template_name = 'admin_panel/admins/list.html'

    def get(self, request):
        admins = get_all_admins()
        return render(request, self.template_name, {'admins': admins})


class AdminCreateView(SuperAdminRequiredMixin, View):
    """Yangi admin qo'shish"""
    template_name = 'admin_panel/admins/form.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        full_name = request.POST.get('full_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        is_super = request.POST.get('is_super') == 'on'

        if not full_name or not phone_number:
            messages.error(request, "Barcha maydonlarni to'ldiring")
            return render(request, self.template_name)

        # Format phone
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if len(phone_number) == 9:
            phone_number = f"+998{phone_number}"
        elif phone_number.startswith('998'):
            phone_number = f"+{phone_number}"

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Bu raqam allaqachon ro'yxatdan o'tgan")
            return render(request, self.template_name)

        create_admin(
            phone_number=phone_number,
            full_name=full_name,
            is_super=is_super
        )
        messages.success(request, f"'{full_name}' admin sifatida qo'shildi")
        return redirect('dashboard:admin_list')


class AdminDeleteView(SuperAdminRequiredMixin, View):
    """Adminni o'chirish"""

    def post(self, request, pk):
        admin = get_object_or_404(User, pk=pk)

        if admin.id == request.user.id:
            messages.error(request, "O'zingizni o'chira olmaysiz")
            return redirect('dashboard:admin_list')

        admin.is_active = False
        admin.save()
        messages.success(request, f"'{admin.full_name}' o'chirildi")
        return redirect('dashboard:admin_list')


# ============== QUIZZES ==============

from apps.quizzes.models import Quiz, Question, Answer
from apps.quizzes.selectors import (
    get_all_quizzes, get_quiz_by_id, get_quiz_with_questions,
    get_question_by_id
)
from apps.quizzes.services import (
    create_quiz, update_quiz, delete_quiz,
    create_question, update_question, delete_question,
    create_answer, update_answer, delete_answer,
    set_correct_answer
)


class QuizListView(AdminRequiredMixin, View):
    """Testlar ro'yxati"""
    template_name = 'admin_panel/quizzes/list.html'

    def get(self, request):
        quizzes = get_all_quizzes()
        return render(request, self.template_name, {'quizzes': quizzes})


class QuizCreateView(AdminRequiredMixin, View):
    """Yangi test yaratish"""
    template_name = 'admin_panel/quizzes/form.html'

    def get(self, request):
        # Faqat quizsi yo'q darslarni ko'rsatish
        lessons = Lesson.objects.filter(
            is_active=True
        ).exclude(
            quiz__isnull=False
        ).order_by('order')

        return render(request, self.template_name, {'lessons': lessons})

    def post(self, request):
        lesson_id = request.POST.get('lesson_id')
        title = request.POST.get('title', '').strip()
        passing_score = request.POST.get('passing_score', 70)
        max_attempts = request.POST.get('max_attempts', 3)

        lessons = Lesson.objects.filter(
            is_active=True
        ).exclude(quiz__isnull=False).order_by('order')

        if not lesson_id or not title:
            messages.error(request, "Barcha maydonlarni to'ldiring")
            return render(request, self.template_name, {'lessons': lessons})

        quiz = create_quiz(
            lesson_id=int(lesson_id),
            title=title,
            passing_score=int(passing_score),
            max_attempts=int(max_attempts)
        )

        messages.success(request, f"'{title}' testi yaratildi")
        return redirect('dashboard:quiz_detail', pk=quiz.pk)


class QuizDetailView(AdminRequiredMixin, View):
    """Test tafsilotlari va savollar"""
    template_name = 'admin_panel/quizzes/detail.html'

    def get(self, request, pk):
        quiz = get_quiz_with_questions(pk)

        if not quiz:
            messages.error(request, "Test topilmadi")
            return redirect('dashboard:quiz_list')

        return render(request, self.template_name, {'quiz': quiz})


class QuizEditView(AdminRequiredMixin, View):
    """Testni tahrirlash"""
    template_name = 'admin_panel/quizzes/form.html'

    def get(self, request, pk):
        quiz = get_quiz_by_id(pk)
        if not quiz:
            messages.error(request, "Test topilmadi")
            return redirect('dashboard:quiz_list')

        return render(request, self.template_name, {'quiz': quiz})

    def post(self, request, pk):
        quiz = get_quiz_by_id(pk)
        if not quiz:
            messages.error(request, "Test topilmadi")
            return redirect('dashboard:quiz_list')

        title = request.POST.get('title', '').strip()
        passing_score = request.POST.get('passing_score', 70)
        max_attempts = request.POST.get('max_attempts', 3)
        is_active = request.POST.get('is_active') == 'on'

        if not title:
            messages.error(request, "Test nomini kiriting")
            return render(request, self.template_name, {'quiz': quiz})

        update_quiz(
            pk,
            title=title,
            passing_score=int(passing_score),
            max_attempts=int(max_attempts),
            is_active=is_active
        )

        messages.success(request, "O'zgarishlar saqlandi")
        return redirect('dashboard:quiz_detail', pk=pk)


class QuizDeleteView(AdminRequiredMixin, View):
    """Testni o'chirish"""

    def post(self, request, pk):
        quiz = get_quiz_by_id(pk)
        if quiz:
            delete_quiz(pk)
            messages.success(request, f"'{quiz.title}' o'chirildi")
        return redirect('dashboard:quiz_list')


class QuestionCreateView(AdminRequiredMixin, View):
    """Yangi savol qo'shish"""
    template_name = 'admin_panel/quizzes/question_form.html'

    def get(self, request, quiz_pk):
        quiz = get_quiz_by_id(quiz_pk)
        if not quiz:
            messages.error(request, "Test topilmadi")
            return redirect('dashboard:quiz_list')

        return render(request, self.template_name, {'quiz': quiz})

    def post(self, request, quiz_pk):
        quiz = get_quiz_by_id(quiz_pk)
        if not quiz:
            messages.error(request, "Test topilmadi")
            return redirect('dashboard:quiz_list')

        text = request.POST.get('text', '').strip()
        order = request.POST.get('order', 0)

        if not text:
            messages.error(request, "Savol matnini kiriting")
            return render(request, self.template_name, {'quiz': quiz})

        # Savol yaratish
        question = create_question(
            quiz_id=quiz_pk,
            text=text,
            order=int(order) if order else 0
        )

        # Javoblarni yaratish
        for i in range(1, 5):
            answer_text = request.POST.get(f'answer_{i}', '').strip()
            is_correct = request.POST.get('correct_answer') == str(i)

            if answer_text:
                create_answer(
                    question_id=question.id,
                    text=answer_text,
                    is_correct=is_correct
                )

        messages.success(request, "Savol qo'shildi")
        return redirect('dashboard:quiz_detail', pk=quiz_pk)


class QuestionEditView(AdminRequiredMixin, View):
    """Savolni tahrirlash"""
    template_name = 'admin_panel/quizzes/question_form.html'

    def get(self, request, quiz_pk, question_pk):
        quiz = get_quiz_by_id(quiz_pk)
        question = get_question_by_id(question_pk)

        if not quiz or not question:
            messages.error(request, "Savol topilmadi")
            return redirect('dashboard:quiz_list')

        # Javoblarni list qilib tayyorlash
        answers_list = list(question.answers.all())
        # 4 tagacha to'ldirish
        while len(answers_list) < 4:
            answers_list.append(None)

        # To'g'ri javob indeksini topish
        correct_index = 1
        for i, ans in enumerate(answers_list):
            if ans and ans.is_correct:
                correct_index = i + 1
                break

        return render(request, self.template_name, {
            'quiz': quiz,
            'question': question,
            'answers_list': answers_list,
            'correct_index': correct_index
        })

    def post(self, request, quiz_pk, question_pk):
        quiz = get_quiz_by_id(quiz_pk)
        question = get_question_by_id(question_pk)

        if not quiz or not question:
            messages.error(request, "Savol topilmadi")
            return redirect('dashboard:quiz_list')

        text = request.POST.get('text', '').strip()
        order = request.POST.get('order', 0)

        if not text:
            messages.error(request, "Savol matnini kiriting")
            return render(request, self.template_name, {
                'quiz': quiz,
                'question': question
            })

        # Savolni yangilash
        update_question(question_pk, text=text, order=int(order) if order else 0)

        # Mavjud javoblarni o'chirish
        question.answers.all().delete()

        # Yangi javoblarni yaratish
        for i in range(1, 5):
            answer_text = request.POST.get(f'answer_{i}', '').strip()
            is_correct = request.POST.get('correct_answer') == str(i)

            if answer_text:
                create_answer(
                    question_id=question_pk,
                    text=answer_text,
                    is_correct=is_correct
                )

        messages.success(request, "Savol yangilandi")
        return redirect('dashboard:quiz_detail', pk=quiz_pk)


class QuestionDeleteView(AdminRequiredMixin, View):
    """Savolni o'chirish"""

    def post(self, request, quiz_pk, question_pk):
        delete_question(question_pk)
        messages.success(request, "Savol o'chirildi")
        return redirect('dashboard:quiz_detail', pk=quiz_pk)