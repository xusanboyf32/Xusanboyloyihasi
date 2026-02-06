from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout
from django.contrib import messages
from django.conf import settings

from .services import initiate_login, verify_otp
from .selectors import get_user_by_id
from core.exceptions import UserNotFoundError, InvalidOTPError, OTPExpiredError


class LoginView(View):
    """Login sahifasi - telefon raqam kiritish"""
    template_name = 'auth/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect(self.get_redirect_url(request.user))
        return render(request, self.template_name)

    def post(self, request):
        phone_number = request.POST.get('phone_number', '').strip()

        # Telefon raqamni formatlash
        phone_number = self.format_phone_number(phone_number)

        if not phone_number:
            messages.error(request, "Telefon raqamni kiriting")
            return render(request, self.template_name)

        try:
            result = initiate_login(phone_number)

            # Session ga user_id ni saqlash (OTP verify uchun)
            request.session['pending_user_id'] = result['user_id']
            request.session['login_phone'] = result['masked_phone']

            return render(request, 'auth/verify_otp.html', {
                'deep_link': result['deep_link'],
                'masked_phone': result['masked_phone'],
                'bot_username': getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot')
            })

        except UserNotFoundError:
            messages.error(request, "Bu raqam tizimda ro'yxatdan o'tmagan")
            return render(request, self.template_name)

    def format_phone_number(self, phone: str) -> str:
        """Telefon raqamni +998XXXXXXXXX formatiga keltirish"""
        phone = ''.join(filter(str.isdigit, phone))

        if phone.startswith('998') and len(phone) == 12:
            return f"+{phone}"
        elif phone.startswith('9') and len(phone) == 9:
            return f"+998{phone}"
        elif len(phone) == 9:
            return f"+998{phone}"

        return f"+{phone}" if phone else ''

    def get_redirect_url(self, user):
        if user.is_admin:
            return 'dashboard:index'
        return 'student:dashboard'


class VerifyOTPView(View):
    """OTP kodni tekshirish"""
    template_name = 'auth/verify_otp.html'

    def get(self, request):
        if 'pending_user_id' not in request.session:
            return redirect('accounts:login')

        return render(request, self.template_name, {
            'masked_phone': request.session.get('login_phone', '')
        })

    def post(self, request):
        user_id = request.session.get('pending_user_id')

        if not user_id:
            messages.error(request, "Sessiya tugagan. Qaytadan urinib ko'ring.")
            return redirect('accounts:login')

        otp_code = request.POST.get('otp_code', '').strip()

        if not otp_code:
            messages.error(request, "Kodni kiriting")
            return render(request, self.template_name, {
                'masked_phone': request.session.get('login_phone', '')
            })

        try:
            user = verify_otp(user_id, otp_code)

            # Session tozalash
            del request.session['pending_user_id']
            if 'login_phone' in request.session:
                del request.session['login_phone']

            # Login qilish
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.full_name}!")

            # Redirect
            if user.is_admin:
                return redirect('dashboard:index')
            return redirect('student:dashboard')

        except InvalidOTPError as e:
            messages.error(request, e.message)
        except OTPExpiredError as e:
            messages.error(request, e.message)

        return render(request, self.template_name, {
            'masked_phone': request.session.get('login_phone', '')
        })


class LogoutView(View):
    """Logout"""

    def get(self, request):
        logout(request)
        messages.info(request, "Tizimdan chiqdingiz")
        return redirect('accounts:login')

    def post(self, request):
        return self.get(request)
