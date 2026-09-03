from typing import List, Dict, Any
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

class MenuCB(CallbackData, prefix="menu"):
    action: str

class LeagueCB(CallbackData, prefix="lg"):
    id: int
    page: int = 1

class FixtureCB(CallbackData, prefix="fx"):
    id: int
    hid: int
    aid: int

class AnalysisCB(CallbackData, prefix="anlz"):
    action: str
    fx: int
    hid: int
    aid: int

def get_start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⚡ Today's Matches", callback_data=MenuCB(action="today").pack()))
    builder.row(InlineKeyboardButton(text="🔴 Live Matches", callback_data=MenuCB(action="live").pack()))
    builder.row(InlineKeyboardButton(text="🏆 Leagues", callback_data=MenuCB(action="leagues").pack()))
    builder.row(InlineKeyboardButton(text="📊 How It Works", callback_data=MenuCB(action="help").pack()))
    return builder.as_markup()

def get_leagues_keyboard(league_counts: Dict[int, tuple]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for lg_id, (name, count) in league_counts.items():
        text = f"{name} ({count})"
        builder.row(InlineKeyboardButton(text=text, callback_data=LeagueCB(id=lg_id, page=1).pack()))
    builder.row(InlineKeyboardButton(text="🔙 Home", callback_data=MenuCB(action="start").pack()))
    return builder.as_markup()

def get_fixtures_keyboard(fixtures: List[Dict[str, Any]], lg_id: int, page: int = 1, total_pages: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for fx in fixtures:
        text = f"{fx['time']}  {fx['home_name']} vs {fx['away_name']}"
        builder.row(InlineKeyboardButton(text=text, callback_data=FixtureCB(id=fx['id'], hid=fx['home_id'], aid=fx['away_id']).pack()))
    
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️ Prev", callback_data=LeagueCB(id=lg_id, page=page-1).pack()))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(text=f"{page} / {total_pages}", callback_data="ignore_pg"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Next ▶️", callback_data=LeagueCB(id=lg_id, page=page+1).pack()))
    
    if nav_row:
        builder.row(*nav_row)
    
    builder.row(InlineKeyboardButton(text="🔙 Leagues", callback_data=MenuCB(action="today").pack()))
    return builder.as_markup()

def get_prediction_keyboard(fx_id: int, hid: int, aid: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🧠 Prediction", callback_data=AnalysisCB(action="predict", fx=fx_id, hid=hid, aid=aid).pack()),
        InlineKeyboardButton(text="📈 Team Form", callback_data=AnalysisCB(action="form", fx=fx_id, hid=hid, aid=aid).pack())
    )
    builder.row(
        InlineKeyboardButton(text="⚔️ H2H", callback_data=AnalysisCB(action="h2h", fx=fx_id, hid=hid, aid=aid).pack()),
        InlineKeyboardButton(text="📊 Statistics", callback_data=AnalysisCB(action="stats", fx=fx_id, hid=hid, aid=aid).pack())
    )
    builder.row(InlineKeyboardButton(text="🔬 Model Details", callback_data=AnalysisCB(action="model", fx=fx_id, hid=hid, aid=aid).pack()))
    builder.row(InlineKeyboardButton(text="🔄 Refresh Analysis", callback_data=FixtureCB(id=fx_id, hid=hid, aid=aid).pack()))
    builder.row(InlineKeyboardButton(text="🔙 Back to Matches", callback_data=MenuCB(action="today").pack()))
    return builder.as_markup()

def get_form_keyboard(fx_id: int, hid: int, aid: int, home_name: str, away_name: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=f"🔴 {home_name}", callback_data="ignore_home"),
        InlineKeyboardButton(text=f"🔵 {away_name}", callback_data="ignore_away")
    )
    builder.row(InlineKeyboardButton(text="🧠 Prediction", callback_data=AnalysisCB(action="predict", fx=fx_id, hid=hid, aid=aid).pack()))
    builder.row(
        InlineKeyboardButton(text="⚔️ H2H", callback_data=AnalysisCB(action="h2h", fx=fx_id, hid=hid, aid=aid).pack()),
        InlineKeyboardButton(text="📊 Statistics", callback_data=AnalysisCB(action="stats", fx=fx_id, hid=hid, aid=aid).pack())
    )
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data=AnalysisCB(action="predict", fx=fx_id, hid=hid, aid=aid).pack()))
    return builder.as_markup()

def get_h2h_keyboard(fx_id: int, hid: int, aid: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📜 More H2H", callback_data=AnalysisCB(action="h2h_more", fx=fx_id, hid=hid, aid=aid).pack()))
    builder.row(
        InlineKeyboardButton(text="🧠 Prediction", callback_data=AnalysisCB(action="predict", fx=fx_id, hid=hid, aid=aid).pack()),
        InlineKeyboardButton(text="📈 Form", callback_data=AnalysisCB(action="form", fx=fx_id, hid=hid, aid=aid).pack())
    )
    builder.row(InlineKeyboardButton(text="📊 Statistics", callback_data=AnalysisCB(action="stats", fx=fx_id, hid=hid, aid=aid).pack()))
    builder.row(InlineKeyboardButton(text="🔙 Back", callback_data=AnalysisCB(action="predict", fx=fx_id, hid=hid, aid=aid).pack()))
    return builder.as_markup()
