from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from telegram_bot.services.api import backend_api

# States
WAITING_PHONE = 1


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/start command"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    args = context.args

    if args and len(args) > 0:
        # Deep link bilan kelgan - token ni saqlash
        token = args[0]
        context.user_data['token'] = token

        # Telefon so'rash - faqat button
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await update.message.reply_text(
            f"👋 Salom, <b>{user.first_name}</b>!\n\n"
            "🔐 Tizimga kirish uchun telefon raqamingizni tasdiqlang.\n\n"
            "👇 Pastdagi tugmani bosing:",
            parse_mode='HTML',
            reply_markup=keyboard
        )
        return WAITING_PHONE
    else:
        # Oddiy /start
        await send_welcome_message(update, context)
        return ConversationHandler.END


async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Telefon raqamni qabul qilish - faqat contact"""
    chat_id = update.effective_chat.id
    token = context.user_data.get('token')

    if not token:
        await update.message.reply_text(
            "❌ Sessiya tugagan.\n\nSaytdan qaytadan urinib ko'ring.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    # Faqat contact qabul qilish
    if not update.message.contact:
        keyboard = ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await update.message.reply_text(
            "❌ Iltimos, pastdagi tugmani bosing:",
            reply_markup=keyboard
        )
        return WAITING_PHONE

    # Telefon raqamni olish
    phone_number = update.message.contact.phone_number
    phone_number = format_phone(phone_number)

    # Loading
    loading_msg = await update.message.reply_text(
        "⏳ Tekshirilmoqda...",
        reply_markup=ReplyKeyboardRemove()
    )

    # Backend ga so'rov
    result = await backend_api.verify_deep_link(token, chat_id, phone_number)

    await loading_msg.delete()

    if result and result.get('success'):
        otp_code = result['otp_code']
        full_name = result.get('user_name', 'Foydalanuvchi')

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Qayta yuborish", callback_data="resend_otp")]
        ])

        await update.message.reply_text(
            f"✅ Tasdiqlandi, <b>{full_name}</b>!\n\n"
            f"🔐 Sizning kodingiz:\n\n"
            f"<code>{otp_code}</code>\n\n"
            f"⏱ Kod 2 daqiqa ichida amal qiladi.\n\n"
            f"👆 Kodni nusxalash uchun ustiga bosing.\n"
            f"👉 Saytga qaytib, kodni kiriting.",
            parse_mode='HTML',
            reply_markup=keyboard
        )

        # Token ni tozalash
        context.user_data.pop('token', None)

    elif result and result.get('error') == 'phone_mismatch':
        await update.message.reply_text(
            "❌ <b>Telefon raqam mos kelmadi!</b>\n\n"
            "Siz saytda boshqa raqam kiritgansiz.\n"
            "Saytga qaytib, to'g'ri raqamni kiriting.",
            parse_mode='HTML'
        )
    elif result and result.get('error') == 'invalid_token':
        await update.message.reply_text(
            "❌ <b>Havola eskirgan!</b>\n\n"
            "Saytdan qaytadan urinib ko'ring.",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            "❌ Xatolik yuz berdi.\n\n"
            "Saytdan qaytadan urinib ko'ring."
        )

    return ConversationHandler.END


async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bekor qilish"""
    context.user_data.pop('token', None)
    await update.message.reply_text(
        "❌ Bekor qilindi.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def send_welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Oddiy salomlashuv xabari"""
    user = update.effective_user

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Saytga o'tish", url="https://eduplatform.uz")]
    ])

    await update.message.reply_text(
        f"👋 Salom, <b>{user.first_name}</b>!\n\n"
        f"Bu <b>EduPlatform</b> rasmiy boti.\n\n"
        f"🔐 Tizimga kirish uchun saytga boring va telefon raqamingizni kiriting.",
        parse_mode='HTML',
        reply_markup=keyboard
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/help command"""
    await update.message.reply_text(
        "ℹ️ <b>Yordam</b>\n\n"
        "Bu bot tizimga kirish uchun tasdiqlash kodlarini yuboradi.\n\n"
        "<b>Qanday foydalanish:</b>\n"
        "1. Saytga boring\n"
        "2. Telefon raqamingizni kiriting\n"
        "3. Telegram havolasini bosing\n"
        "4. Telefon raqamingizni tasdiqlang\n"
        "5. Botdan kelgan kodni saytga kiriting\n\n"
        "/start - Boshlash\n"
        "/help - Yordam\n"
        "/cancel - Bekor qilish",
        parse_mode='HTML'
    )


def format_phone(phone: str) -> str:
    """Telefon raqamni formatlash"""
    phone = ''.join(filter(str.isdigit, phone))

    if phone.startswith('998') and len(phone) == 12:
        return f"+{phone}"
    elif len(phone) == 9:
        return f"+998{phone}"

    return f"+{phone}" if phone else ''