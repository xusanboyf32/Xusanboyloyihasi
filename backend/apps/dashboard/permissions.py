from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


class AdminRequiredMixin:
    """Admin bo'lishi shart"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Tizimga kiring")
            return redirect('accounts:login')

        if not request.user.is_admin:
            messages.error(request, "Sizda ruxsat yo'q")
            return redirect('accounts:login')

        return super().dispatch(request, *args, **kwargs)


class SuperAdminRequiredMixin:
    """Super admin bo'lishi shart"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Tizimga kiring")
            return redirect('accounts:login')

        if not request.user.is_super_admin:
            messages.error(request, "Faqat super admin uchun")
            return redirect('dashboard:index')

        return super().dispatch(request, *args, **kwargs)
