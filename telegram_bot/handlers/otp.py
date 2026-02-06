from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from telegram_bot.services.api import backend_api


async def resend_otp_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback: OTP ni qayta yuborish"""

    query = update.callback_query
    await query.answer()

    chat_id = update.effective_chat.id

    # Loading
    await query.edit_message_text("⏳ Yangi kod yuborilmoqda...")

    # Backend ga so'rov
    result = await backend_api.resend_otp(chat_id)

    if result and result.get('success'):
        otp_code = result.get('otp_code')

        message = (
            f"🔐 Yangi tasdiqlash kodingiz:\n\n"
            f"<code>{otp_code}</code>\n\n"
            f"⏱ Kod 2 daqiqa ichida amal qiladi.\n\n"
            f"☝️ Kodni saytdagi maydonchaga kiriting."
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Qayta yuborish", callback_data="resend_otp")]
        ])

        await query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=keyboard
        )
    else:
        await query.edit_message_text(
            "❌ Xatolik yuz berdi.\n\n"
            "Iltimos, saytdan qaytadan login qiling.",
            parse_mode='HTML'
        )