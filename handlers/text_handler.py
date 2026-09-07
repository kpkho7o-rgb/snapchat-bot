from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import OWNER_ID
from access_store import is_allowed
from states import AnalysisStates
from services.gemini_service import analyze_text

router = Router()


@router.message(AnalysisStates.waiting_text, F.text & ~F.text.startswith("/"))
async def handle_text(message: Message, state: FSMContext):
    if not is_allowed(message.from_user.id, OWNER_ID):
        return

    thinking = await message.answer("انتظر قليلاً لكي أحلل ..")
    try:
        result = await analyze_text(message.text)
        await thinking.edit_text(result)
    except Exception as e:
        await thinking.edit_text(f"حدث خطأ أثناء التحليل: {e}")
    finally:
        await state.clear()
