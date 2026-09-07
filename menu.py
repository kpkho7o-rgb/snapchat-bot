from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import OWNER_ID
from access_store import is_allowed
from states import AnalysisStates

router = Router()

PROMPTS = {
    "mode_photo": "أرسل الصور التي تريد أن أحللها",
    "mode_video": "أرسل المقطع الذي تريد أن أحلله",
    "mode_text": "أرسل المحادثة (انسخ كلامه أو صورة للشات) التي تريد أن أحللها",
}

STATES = {
    "mode_photo": AnalysisStates.waiting_photo,
    "mode_video": AnalysisStates.waiting_video,
    "mode_text": AnalysisStates.waiting_text,
}


@router.callback_query()
async def handle_menu_choice(callback: CallbackQuery, state: FSMContext):
    if not is_allowed(callback.from_user.id, OWNER_ID):
        await callback.answer("هذا البوت خاص.", show_alert=True)
        return

    choice = callback.data
    if choice not in PROMPTS:
        await callback.answer()
        return

    await state.set_state(STATES[choice])
    await callback.message.answer(PROMPTS[choice])
    await callback.answer()
