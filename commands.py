from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.fsm.context import FSMContext

from config import OWNER_ID
from access_store import is_allowed

router = Router()

WELCOME_TEXT = (
    "مرحباً ببوت الأب ميشش لتحليل مخالفات عينات السناب  😋\n\n"
    "اختر نوع التحليل الذي تريده من يا مز:"
)

PRIVATE_BOT_TEXT = (
    "هذا البوت خاص بفحلك ميش.\n"
    "تم إرسال طلبك إلى ميشش انتضره."
)

WELCOME_GIF_PATH = "welcome.mp4"


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="تحليل صورة", callback_data="mode_photo")],
            [InlineKeyboardButton(text="تحليل مقاطع", callback_data="mode_video")],
            [InlineKeyboardButton(text="تحليل محادثات", callback_data="mode_text")],
        ]
    )


def approval_kb(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="موافقة", callback_data=f"approve_{user_id}"),
                InlineKeyboardButton(text="رفض", callback_data=f"deny_{user_id}"),
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user

    if is_allowed(user.id, OWNER_ID):
        await state.clear()
        try:
            gif = FSInputFile(WELCOME_GIF_PATH)
            await message.answer_animation(
                animation=gif,
                caption=WELCOME_TEXT,
                reply_markup=main_menu_kb(),
            )
        except Exception:
            # لو الملف مو موجود أو صار خطأ، يرسل النص بس بدون ما يوقف البوت
            await message.answer(WELCOME_TEXT, reply_markup=main_menu_kb())
        return

    await message.answer(PRIVATE_BOT_TEXT)

    username_line = f"@{user.username}" if user.username else "لا يوجد يوزر"
    notify_text = (
        "طلب استخدام جديد للبوت\n\n"
        f"الاسم: {user.full_name}\n"
        f"اليوزر: {username_line}\n"
        f"الآيدي: <code>{user.id}</code>"
    )
    try:
        await bot.send_message(OWNER_ID, notify_text, reply_markup=approval_kb(user.id))
    except Exception:
        pass