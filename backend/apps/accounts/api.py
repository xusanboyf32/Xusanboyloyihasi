import json

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings

from .services import create_otp_for_user, set_telegram_chat_id, verify_otp
from .selectors import get_user_by_id, get_user_by_telegram_chat_id
from core.utils import verify_deep_link_token
from core.exceptions import UserNotFoundError, InvalidOTPError, OTPExpiredError


def require_bot_token(view_func):
    """Bot API token tekshiruvchi decorator"""

    def wrapper(request, *args, **kwargs):
        token = request.headers.get('X-Bot-Token')
        if token != settings.BOT_API_TOKEN:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


@method_decorator([csrf_exempt, require_bot_token], name='dispatch')
class VerifyDeepLinkAPI(View):
    """Deep link + telefon tekshirish va OTP yaratish"""

    def post(self, request):
        try:
            data = json.loads(request.body)
            token = data.get('token')
            chat_id = data.get('chat_id')
            phone_number = data.get('phone_number')

            if not token or not chat_id or not phone_number:
                return JsonResponse({
                    'success': False,
                    'error': 'token, chat_id va phone_number talab qilinadi'
                }, status=400)

            # Token ni tekshirish
            user_id = verify_deep_link_token(token)
            if not user_id:
                return JsonResponse({
                    'success': False,
                    'error': 'invalid_token'
                }, status=400)

            # User ni olish
            user = get_user_by_id(user_id)
            if not user:
                return JsonResponse({
                    'success': False,
                    'error': 'user_not_found'
                }, status=404)

            # Telefon raqamni tekshirish
            if user.phone_number != phone_number:
                return JsonResponse({
                    'success': False,
                    'error': 'phone_mismatch'
                }, status=400)

            # Chat ID ni saqlash
            set_telegram_chat_id(user.id, chat_id)

            # OTP yaratish
            otp = create_otp_for_user(user.id)

            return JsonResponse({
                'success': True,
                'otp_code': otp.code,
                'expires_in': settings.OTP_EXPIRE_SECONDS,
                'user_name': user.full_name
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'invalid_json'
            }, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


@method_decorator([csrf_exempt, require_bot_token], name='dispatch')
class CheckUserAPI(View):
    """
    User mavjudligini tekshirish (telefon yoki chat_id bo'yicha)
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')

            if not chat_id:
                return JsonResponse({
                    'success': False,
                    'error': 'chat_id talab qilinadi'
                }, status=400)

            user = get_user_by_telegram_chat_id(chat_id)

            if user:
                return JsonResponse({
                    'success': True,
                    'exists': True,
                    'user': {
                        'id': user.id,
                        'full_name': user.full_name,
                        'phone_number': user.phone_number,
                        'role': user.role
                    }
                })

            return JsonResponse({
                'success': True,
                'exists': False
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)


@method_decorator([csrf_exempt, require_bot_token], name='dispatch')
class ResendOTPAPI(View):
    """
    OTP qayta yuborish (agar user allaqachon chat_id bilan bog'langan bo'lsa)
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
            chat_id = data.get('chat_id')

            if not chat_id:
                return JsonResponse({
                    'success': False,
                    'error': 'chat_id talab qilinadi'
                }, status=400)

            user = get_user_by_telegram_chat_id(chat_id)

            if not user:
                return JsonResponse({
                    'success': False,
                    'error': 'Foydalanuvchi topilmadi'
                }, status=404)

            otp = create_otp_for_user(user.id)

            return JsonResponse({
                'success': True,
                'otp_code': otp.code,
                'expires_in': settings.OTP_EXPIRE_SECONDS,
                'user_name': user.full_name
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)




