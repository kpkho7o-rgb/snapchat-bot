from aiogram.fsm.state import State, StatesGroup


class AnalysisStates(StatesGroup):
    waiting_photo = State()
    waiting_video = State()
    waiting_text = State()
