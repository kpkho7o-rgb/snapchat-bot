from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import OWNER_ID
from access_store import is_allowed
from states import AnalysisStates
from services.gemini_service import analyze_media

router = Router()

MAX_VIDEO_MB = 20


@router.message(AnalysisStates.waiting_photo, F.photo)
async def handle_photo(message: Message, bot: Bot, state: FSMContext):
    if not is_allowed(message.from_user.id, OWNER_ID):
        return

    thinking = await message.answer("انتظر قليلاً لكي أحلل ذاالقواد ..")
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_bytes_io = await bot.download_file(file.file_path)
        file_bytes = file_bytes_io.read()

        result = await analyze_media(
            file_bytes, "image/jpeg", caption=message.caption or ""
        )
        await thinking.edit_text(result)
    except Exception as e:
        await thinking.edit_text(f"حدث خطأ أثناء تحليل الصورة: {e}")
    finally:
        await state.clear()


@router.message(AnalysisStates.waiting_video, F.video)
async def handle_video(message: Message, bot: Bot, state: FSMContext):
    if not is_allowed(message.from_user.id, OWNER_ID):
        return

    if message.video.file_size and message.video.file_size > MAX_VIDEO_MB * 1024 * 1024:
        await message.answer(
            f"حجم المقطع كبير جداً لهذا الإصدار (الحد الأقصى {MAX_VIDEO_MB}MB)."
        )
        await state.clear()
        return

    thinking = await message.answer("انتظر قليلاً لكي أحلل ذاالقواد  ..")
    try:
        file = await bot.get_file(message.video.file_id)
        file_bytes_io = await bot.download_file(file.file_path)
        file_bytes = file_bytes_io.read()

        result = await analyze_media(
            file_bytes, "video/mp4", caption=message.caption or ""
        )
        await thinking.edit_text(result)
    except Exception as e:
        await thinking.edit_text(f"حدث خطأ أثناء تحليل المقطع: {e}")
    finally:
        await state.clear()
