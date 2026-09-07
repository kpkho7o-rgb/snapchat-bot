import logging

from aiogram import Router, Bot
from aiogram.types import CallbackQuery

from config import OWNER_ID
from access_store import allow_user

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(lambda c: c.data and c.data.startswith(("approve_", "deny_")))
async def handle_approval(callback: CallbackQuery, bot: Bot):
    try:
        if callback.from_user.id != OWNER_ID:
            await callback.answer("هذا الإجراء للمالك فقط.", show_alert=True)
            return

        await callback.answer()

        action, user_id_str = callback.data.split("_", 1)
        user_id = int(user_id_str)

        if action == "approve":
            allow_user(user_id)
            await callback.message.edit_text(callback.message.text + "\n\nتمت الموافقة.")
            try:
                await bot.send_message(
                    user_id,
                    "تمت الموافقة على طلبك، يمكنك الآن استخدام البوت. أرسل /start للبدء.",
                )
            except Exception as e:
                logger.warning(f"Could not notify approved user {user_id}: {e}")
        else:
            await callback.message.edit_text(callback.message.text + "\n\nتم الرفض.")
            try:
                await bot.send_message(user_id, "تم رفض طلب استخدامك للبوت.")
            except Exception as e:
                logger.warning(f"Could not notify denied user {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error handling approval callback: {e}")
        try:
            await callback.answer("حدث خطأ، جرب من رسالة طلب جديدة.", show_alert=True)
        except Exception:
            pass
