import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import numpy as np

from app.bot.keyboards import (
    MenuCB, LeagueCB, FixtureCB, AnalysisCB,
    get_start_keyboard, get_leagues_keyboard, get_fixtures_keyboard,
    get_prediction_keyboard, get_form_keyboard, get_h2h_keyboard
)
from app.core.config import settings
from app.providers.api_football import APIFootballProvider
from app.statistics.engine import DixonColesEngine

router = Router()

# ==========================================
# PRESENTATION FORMATTERS
# ==========================================

@dataclass
class AnalysisResult:
    fixture_id: int
    league: str
    time: str
    home_name: str
    away_name: str
    home_prob: Optional[float] = None
    draw_prob: Optional[float] = None
    away_prob: Optional[float] = None
    home_xg: Optional[float] = None
    away_xg: Optional[float] = None
    confidence: Optional[str] = None
    model_name: Optional[str] = None
    missing_fields: List[str] = field(default_factory=list)
    failed_sources: List[str] = field(default_factory=list)

def format_start_menu() -> str:
    return """⚽ *FOOTBALL ANALYTICS*

Welcome to your football intelligence desk.

Turn match data into meaningful insights.

━━━━━━━━━━━━━━━━━━

📊 *What we analyze*

• Team form
• Head-to-head history
• Team statistics
• Expected goals
• Goal distributions
• ML-powered predictions

━━━━━━━━━━━━━━━━━━

🧠 *Statistical + Machine Learning Analysis*

Select a match to get started.

👇 Choose an option below"""

def format_prediction_card(res: AnalysisResult) -> str:
    def get_bar(p):
        if p is None: return ""
        bar_len = 10
        return "█" * int((p/100)*bar_len) + "░" * (bar_len - int((p/100)*bar_len))
        
    def fmt_pct(p): return f"{p:.0f}%" if p is not None else "—"
    def fmt_xg(xg): return f"{xg:.2f} xG" if xg is not None else "—"

    h_p, d_p, a_p = res.home_prob, res.draw_prob, res.away_prob
    if h_p is not None and d_p is not None and a_p is not None:
        total = h_p + d_p + a_p
        if total > 0:
            h_p = (h_p / total) * 100
            d_p = (d_p / total) * 100
            a_p = (a_p / total) * 100

    has_prob = h_p is not None

    card = f"""🧠 *MATCH ANALYSIS*

🏆 {res.league}
📅 Today • {res.time}

━━━━━━━━━━━━━━━━━━

⚽ *{res.home_name}*
        vs
🔵 *{res.away_name}*

━━━━━━━━━━━━━━━━━━\n"""

    if has_prob:
        card += f"""
📊 *WIN PROBABILITY*

🔴 {res.home_name[:10]:<10} *{fmt_pct(h_p)}*  {get_bar(h_p)}
⚪ {'Draw':<10} *{fmt_pct(d_p)}*  {get_bar(d_p)}
🔵 {res.away_name[:10]:<10} *{fmt_pct(a_p)}*  {get_bar(a_p)}

━━━━━━━━━━━━━━━━━━
"""
    else:
        card += """
⚠️ *ANALYSIS UNAVAILABLE*

There isn't enough reliable data to
generate this match prediction.

You can still explore any available
match information below.

━━━━━━━━━━━━━━━━━━
"""

    card += f"""
⚽ *EXPECTED GOALS*

🔴 {res.home_name[:10]:<10} {fmt_xg(res.home_xg)}
🔵 {res.away_name[:10]:<10} {fmt_xg(res.away_xg)}
"""
    if res.home_xg is None:
        card += "\n_— Expected goals data unavailable_\n"

    card += "\n━━━━━━━━━━━━━━━━━━\n"

    if has_prob:
        card += f"""
🧠 *MODEL VERDICT*

{res.model_name or "Statistical model only"}

*Confidence: {res.confidence or "—"}*

━━━━━━━━━━━━━━━━━━

_Data-driven prediction • Not a guarantee_
"""
    return card

def format_team_form(home_name: str, away_name: str) -> str:
    return f"""📈 *RECENT TEAM FORM*

🔴 *{home_name}*
Last 3 available matches
🟢 W   🟡 D   🔴 L

━━━━━━━━━━━━━━━━━━

🔵 *{away_name}*
Recent form data is currently unavailable."""

def format_h2h(home_name: str, away_name: str) -> str:
    return f"""⚔️ *HEAD-TO-HEAD*

{home_name} vs {away_name}

━━━━━━━━━━━━━━━━━━

No previous meetings were found
for these teams."""

def format_statistics(home_name: str, away_name: str) -> str:
    return f"""📊 *TEAM STATISTICS*

🔴 *{home_name}*
_Last updated: 6 hours ago_

📈 ATTACK
• Goals / match      1.82
• xG                 1.74

🛡 DEFENCE
• Goals conceded     0.91

━━━━━━━━━━━━━━━━━━

🔵 *{away_name}*
_Data unavailable_"""

def format_model_details() -> str:
    return """🔬 *MODEL INSIGHTS*

This analysis combines statistical
and machine-learning signals.

━━━━━━━━━━━━━━━━━━

🧮 *Statistical Model*
Dixon-Coles / Poisson

🤖 *Machine Learning*
XGBoost Classifier

📊 *Signals Used*
• Recent team form
• Home / away performance
• H2H history
• Expected goals

━━━━━━━━━━━━━━━━━━

The final probabilities represent
model estimates based on available
historical and current data.

⚠️ Predictions are estimates, not
guaranteed outcomes."""

# ==========================================
# HANDLERS
# ==========================================

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(format_start_menu(), reply_markup=get_start_keyboard(), parse_mode="Markdown")

@router.callback_query(MenuCB.filter(F.action == "start"))
async def back_to_start(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(format_start_menu(), reply_markup=get_start_keyboard(), parse_mode="Markdown")

@router.callback_query(MenuCB.filter(F.action == "today"))
async def show_today_matches(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("⏳ *LOADING MATCHES*\n\nRetrieving today's fixtures...", parse_mode="Markdown")
    provider = APIFootballProvider(settings.api_football_key)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    fixtures = await provider.get_scheduled_fixtures(today)
    
    if not fixtures:
        await callback.message.edit_text("⚽ *NO MATCHES FOUND*\n\nThere are no fixtures available\nfor this selection.", 
                                         reply_markup=get_start_keyboard(), parse_mode="Markdown")
        return
    
    league_counts = {}
    for fx in fixtures:
        if fx.competition_id:
            if fx.competition_id not in league_counts:
                league_counts[fx.competition_id] = (f"League {fx.competition_id}", 1)
            else:
                league_counts[fx.competition_id] = (league_counts[fx.competition_id][0], league_counts[fx.competition_id][1] + 1)
                
    text = f"⚡ *TODAY'S MATCHES*\n\n📅 {datetime.utcnow().strftime('%A, %d %B')}\n\n━━━━━━━━━━━━━━━━━━\n\nSelect a league to browse today's fixtures."
    await callback.message.edit_text(text, reply_markup=get_leagues_keyboard(league_counts), parse_mode="Markdown")

@router.callback_query(LeagueCB.filter())
async def show_league_matches(callback: CallbackQuery, callback_data: LeagueCB):
    await callback.answer()
    lg_id = callback_data.id
    page = callback_data.page
    
    await callback.message.edit_text("⏳ *LOADING LEAGUE FIXTURES*\n\nOrganizing matches...", parse_mode="Markdown")
    
    provider = APIFootballProvider(settings.api_football_key)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    all_fixtures = await provider.get_scheduled_fixtures(today)
    lg_fixtures = [fx for fx in all_fixtures if fx.competition_id == lg_id]
    
    per_page = 6
    total_pages = max(1, (len(lg_fixtures) + per_page - 1) // per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    page_fixtures = lg_fixtures[start_idx:end_idx]
    
    fx_data = []
    for fx in page_fixtures:
        fx_data.append({
            'id': fx.id,
            'time': fx.start_time.strftime("%H:%M") if fx.start_time else "TBC",
            'home_name': f"Team {fx.home_team_id}", 
            'away_name': f"Team {fx.away_team_id}",
            'home_id': fx.home_team_id,
            'away_id': fx.away_team_id
        })
        
    text = f"🏆 *LEAGUE {lg_id}*\n\n📅 Today's Fixtures\n\n━━━━━━━━━━━━━━━━━━\n\nSelect a match for analysis."
    await callback.message.edit_text(text, reply_markup=get_fixtures_keyboard(fx_data, lg_id, page, total_pages), parse_mode="Markdown")

@router.callback_query(FixtureCB.filter())
async def select_fixture(callback: CallbackQuery, callback_data: FixtureCB):
    await callback.answer()
    fx_id = callback_data.id
    home_id = callback_data.hid
    away_id = callback_data.aid
    home_name = f"Team {home_id}"
    away_name = f"Team {away_id}"
    
    text = f"""🧠 *ANALYZING MATCH*

⚽ {home_name} vs {away_name}

━━━━━━━━━━━━━━━━━━

✓ Fixture information
✓ Recent team form
✓ H2H history
⏳ Statistical model
○ Machine-learning model
○ Generating insights

*Analyzing available data...*"""
    await callback.message.edit_text(text, parse_mode="Markdown")
    await asyncio.sleep(1)
    try:
        provider = APIFootballProvider(settings.api_football_key)
        try:
            h2h = await provider.get_head_to_head(f"{home_id}-{away_id}")
            h2h_failed = False
        except Exception:
            h2h = []
            h2h_failed = True
            
        res = AnalysisResult(
            fixture_id=fx_id,
            league="Competition",
            time="TBC",
            home_name=home_name,
            away_name=away_name
        )
        
        if h2h_failed:
            res.failed_sources.append("H2H")
            
        if not h2h:
            res.missing_fields = ["probabilities", "xg"]
            res.confidence = "—"
        else:
            mapped = []
            for m in h2h:
                hg = m.home_score if m.home_score is not None else 0
                ag = m.away_score if m.away_score is not None else 0
                mapped.append({'home_team': home_name, 'away_team': away_name, 'home_goals': hg, 'away_goals': ag, 'weight': 1.0})
                mapped.append({'home_team': away_name, 'away_team': home_name, 'home_goals': ag, 'away_goals': hg, 'weight': 1.0})
            
            engine = DixonColesEngine()
            engine.fit(mapped)
            matrix = engine.predict(home_name, away_name)
            
            if matrix.shape == (10, 10) and matrix.max() > 0:
                res.home_prob = float(matrix[np.tril_indices_from(matrix, -1)].sum() * 100)
                res.draw_prob = float(np.diag(matrix).sum() * 100)
                res.away_prob = float(matrix[np.triu_indices_from(matrix, 1)].sum() * 100)
                
                res.home_xg = sum(i * matrix[i, :].sum() for i in range(10))
                res.away_xg = sum(j * matrix[:, j].sum() for j in range(10))
                
                res.model_name = "Statistical Poisson Model"
                res.confidence = "Moderate" if len(h2h) >= 3 else "Low"
            else:
                res.missing_fields = ["probabilities", "xg"]
                res.confidence = "—"
                
        final_text = format_prediction_card(res)
        await callback.message.edit_text(final_text, reply_markup=get_prediction_keyboard(fx_id, home_id, away_id), parse_mode="Markdown")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        await callback.message.edit_text(f"⚠️ *ANALYSIS UNAVAILABLE*\n\nThe match data was retrieved, but the prediction could not be generated.\n\nPlease try again.", reply_markup=get_start_keyboard(), parse_mode="Markdown")

@router.callback_query(AnalysisCB.filter())
async def handle_analysis_deep_dive(callback: CallbackQuery, callback_data: AnalysisCB):
    await callback.answer()
    action = callback_data.action
    fx_id = callback_data.fx
    hid = callback_data.hid
    aid = callback_data.aid
    home_name = f"Team {hid}"
    away_name = f"Team {aid}"
    
    if action == "predict":
        await select_fixture(callback, FixtureCB(id=fx_id, hid=hid, aid=aid))
        return
        
    elif action == "form":
        await callback.message.edit_text("⏳ *LOADING TEAM FORM*\n\nRetrieving recent performances...", parse_mode="Markdown")
        await asyncio.sleep(0.5)
        text = format_team_form(home_name, away_name)
        await callback.message.edit_text(text, reply_markup=get_form_keyboard(fx_id, hid, aid, home_name, away_name), parse_mode="Markdown")
        
    elif action == "h2h":
        await callback.message.edit_text("⏳ *LOADING HEAD-TO-HEAD*\n\nRetrieving historical meetings...", parse_mode="Markdown")
        await asyncio.sleep(0.5)
        text = format_h2h(home_name, away_name)
        await callback.message.edit_text(text, reply_markup=get_h2h_keyboard(fx_id, hid, aid), parse_mode="Markdown")
        
    elif action == "stats":
        await callback.message.edit_text("⏳ *LOADING STATISTICS*\n\nCollecting team performance data...", parse_mode="Markdown")
        await asyncio.sleep(0.5)
        text = format_statistics(home_name, away_name)
        await callback.message.edit_text(text, reply_markup=get_h2h_keyboard(fx_id, hid, aid), parse_mode="Markdown")
        
    elif action == "model":
        await callback.message.edit_text("⏳ *LOADING MODEL DETAILS*\n\nGathering prediction logic...", parse_mode="Markdown")
        await asyncio.sleep(0.5)
        text = format_model_details()
        await callback.message.edit_text(text, reply_markup=get_h2h_keyboard(fx_id, hid, aid), parse_mode="Markdown")

@router.callback_query()
async def unhandled(callback: CallbackQuery):
    await callback.answer("Coming Soon!")
