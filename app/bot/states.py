from aiogram.fsm.state import State, StatesGroup

class AnalysisFlow(StatesGroup):
    waiting_for_competition = State()
    waiting_for_home_team = State()
    waiting_for_away_team = State()
