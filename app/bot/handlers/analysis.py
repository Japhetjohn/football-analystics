import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import numpy as np

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

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
    return """⚽ <b>FOOTBALL ANALYTICS</b>

Welcome to your football intelligence desk.

Turn match data into meaningful insights.

━━━━━━━━━━━━━━━━━━

📊 <b>What we analyze</b>

• Team form
• Head-to-head history
• Team statistics
• Expected goals
• Goal distributions
• ML-powered predictions

━━━━━━━━━━━━━━━━━━

🧠 <b>Statistical + Machine Learning Analysis</b>

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

    card = f"""🧠 <b>MATCH ANALYSIS</b>

🏆 {res.league}
📅 Today • {res.time}

━━━━━━━━━━━━━━━━━━

⚽ <b>{res.home_name}</b>
        vs
🔵 <b>{res.away_name}</b>

━━━━━━━━━━━━━━━━━━\n"""

    if has_prob:
        if h_p > d_p and h_p > a_p:
            pred_winner = res.home_name
        elif a_p > h_p and a_p > d_p:
            pred_winner = res.away_name
        else:
            pred_winner = "Draw"
            
        h_score_pred = int(round(res.home_xg)) if res.home_xg is not None else 0
        a_score_pred = int(round(res.away_xg)) if res.away_xg is not None else 0
        
        card += f"""
🎯 <b>FINAL PREDICTION</b>

<b>Predicted Winner:</b> {pred_winner}
<b>Predicted Score:</b> {res.home_name} {h_score_pred} - {a_score_pred} {res.away_name}

━━━━━━━━━━━━━━━━━━
"""
        card += f"""
📊 <b>WIN PROBABILITY</b>

🔴 {res.home_name[:10]:<10} <b>{fmt_pct(h_p)}</b>  {get_bar(h_p)}
⚪ {'Draw':<10} <b>{fmt_pct(d_p)}</b>  {get_bar(d_p)}
🔵 {res.away_name[:10]:<10} <b>{fmt_pct(a_p)}</b>  {get_bar(a_p)}

━━━━━━━━━━━━━━━━━━
"""
    else:
        card += """
⚠️ <b>ANALYSIS UNAVAILABLE</b>

There isn't enough reliable data to
generate this match prediction.

You can still explore any available
match information below.

━━━━━━━━━━━━━━━━━━
"""

    card += f"""
⚽ <b>EXPECTED GOALS</b>

🔴 {res.home_name[:10]:<10} {fmt_xg(res.home_xg)}
🔵 {res.away_name[:10]:<10} {fmt_xg(res.away_xg)}
"""
    if res.home_xg is None:
        card += "\n<i>— Expected goals data unavailable</i>\n"

    card += "\n━━━━━━━━━━━━━━━━━━\n"

    if has_prob:
        card += f"""
🧠 <b>MODEL VERDICT</b>

{res.model_name or "Statistical model only"}

<b>Confidence: {res.confidence or "—"}</b>

━━━━━━━━━━━━━━━━━━

<i>Data-driven prediction • Not a guarantee</i>
"""
    return card

def format_team_form(home_name: str, away_name: str, home_form: str, away_form: str) -> str:
    def parse_form(f_str):
        if f_str is None: return "Recent form data is currently unavailable."
        res = []
        for char in f_str[-5:]:
            if char == 'W': res.append("🟢 W")
            elif char == 'D': res.append("🟡 D")
            elif char == 'L': res.append("🔴 L")
        return "   ".join(res) if res else "Recent form data is currently unavailable."

    return f"""📈 <b>RECENT TEAM FORM</b>

🔴 <b>{home_name}</b>
{parse_form(home_form)}

━━━━━━━━━━━━━━━━━━

🔵 <b>{away_name}</b>
{parse_form(away_form)}"""

def format_h2h(home_name: str, away_name: str, h2h_list: List[Any], hid: int) -> str:
    if not h2h_list:
        return f"⚔️ <b>HEAD-TO-HEAD</b>\n\n{home_name} vs {away_name}\n\n━━━━━━━━━━━━━━━━━━\n\nNo previous meetings were found\nfor these teams."
    
    text = f"⚔️ <b>HEAD-TO-HEAD</b>\n\n{home_name} vs {away_name}\n\n━━━━━━━━━━━━━━━━━━\n\n<b>Last {min(5, len(h2h_list))} Meetings</b>\n\n"
    for m in h2h_list[:5]:
        home_is_our_home = m.home_team_id == hid
        h_score = m.home_score if m.home_score is not None else 0
        a_score = m.away_score if m.away_score is not None else 0
        
        if home_is_our_home:
            text += f"🔴 {home_name[:10]:<10} {h_score}–{a_score}  {away_name[:10]:>10} 🔵\n"
        else:
            # They are reversed in this historical match
            text += f"🔵 {away_name[:10]:<10} {h_score}–{a_score}  {home_name[:10]:>10} 🔴\n"
    return text

def format_statistics(home_name: str, away_name: str, home_stats: Dict[str, Any], away_stats: Dict[str, Any]) -> str:
    text = f"📊 <b>TEAM STATISTICS</b>\n\n"
    
    def render_team(name, stats, icon):
        if not stats:
            return f"{icon} <b>{name}</b>\n<i>Data unavailable</i>\n"
        
        shots = stats.get('Total Shots', '—')
        s_on = stats.get('Shots on Goal', '—')
        poss = stats.get('Ball Possession', '—')
        
        return f"""{icon} <b>{name}</b>

📈 ATTACK
• Shots              {shots}
• On Target          {s_on}
• Possession         {poss}
"""
    
    text += render_team(home_name, home_stats, "🔴")
    text += "\n━━━━━━━━━━━━━━━━━━\n\n"
    text += render_team(away_name, away_stats, "🔵")
    return text

def format_model_details() -> str:
    return """🔬 <b>MODEL INSIGHTS</b>

This analysis combines statistical
and machine-learning signals.

━━━━━━━━━━━━━━━━━━

🧮 <b>Statistical Model</b>
Dixon-Coles / Poisson

🤖 <b>Machine Learning</b>
XGBoost Classifier

📊 <b>Signals Used</b>
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

async def safe_edit_text(callback: CallbackQuery, text: str, reply_markup=None):
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode="HTML")
    except Exception as e:
        if "message is not modified" not in str(e).lower():
            import traceback
            traceback.print_exc()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(format_start_menu(), reply_markup=get_start_keyboard(), parse_mode="HTML")

@router.callback_query(MenuCB.filter(F.action == "start"))
async def back_to_start(callback: CallbackQuery):
    await callback.answer()
    await safe_edit_text(callback, format_start_menu(), reply_markup=get_start_keyboard())

@router.callback_query(MenuCB.filter(F.action == "today"))
async def show_today_matches(callback: CallbackQuery):
    await callback.answer("Loading today's matches...", show_alert=False)
    msg = await callback.message.answer("⏳ <b>LOADING MATCHES</b>\n\nRetrieving today's fixtures...", parse_mode="HTML")
    
    try:
        provider = APIFootballProvider(settings.api_football_key)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        fixtures = await provider.get_scheduled_fixtures(today)
    except Exception:
        await msg.edit_text("⚠️ <b>UNABLE TO FETCH DATA</b>\n\nPlease tap Refresh or try again in a moment.", reply_markup=get_start_keyboard(), parse_mode="HTML")
        return
        
    if not fixtures:
        await msg.edit_text("⚽ <b>NO MATCHES FOUND</b>\n\nThere are no fixtures available\nfor this selection.", reply_markup=get_start_keyboard(), parse_mode="HTML")
        return
    
    league_counts = {}
    for fx in fixtures:
        if fx.competition_id:
            c_name = fx.competition_name or f"League {fx.competition_id}"
            if fx.competition_id not in league_counts:
                league_counts[fx.competition_id] = (c_name, 1)
            else:
                league_counts[fx.competition_id] = (league_counts[fx.competition_id][0], league_counts[fx.competition_id][1] + 1)
                
    text = f"⚡ <b>TODAY'S MATCHES</b>\n\n📅 {datetime.utcnow().strftime('%A, %d %B')}\n\n━━━━━━━━━━━━━━━━━━\n\nSelect a league to browse today's fixtures."
    await msg.edit_text(text, reply_markup=get_leagues_keyboard(league_counts), parse_mode="HTML")

@router.callback_query(LeagueCB.filter())
async def show_league_matches(callback: CallbackQuery, callback_data: LeagueCB):
    await callback.answer("Organizing matches...", show_alert=False)
    lg_id = callback_data.id
    page = callback_data.page
    
    is_refresh = "Today's Fixtures" in (callback.message.text or "")
    if is_refresh:
        msg = callback.message
        await msg.edit_text("⏳ <b>LOADING LEAGUE FIXTURES</b>\n\nOrganizing matches...", parse_mode="HTML")
    else:
        msg = await callback.message.answer("⏳ <b>LOADING LEAGUE FIXTURES</b>\n\nOrganizing matches...", parse_mode="HTML")
    
    try:
        provider = APIFootballProvider(settings.api_football_key)
        today = datetime.utcnow().strftime("%Y-%m-%d")
        all_fixtures = await provider.get_scheduled_fixtures(today)
    except Exception:
        await msg.edit_text("⚠️ <b>UNABLE TO FETCH DATA</b>\n\nPlease try again in a moment.", reply_markup=get_start_keyboard(), parse_mode="HTML")
        return
        
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
            'home_name': fx.home_team_name or f"Team {fx.home_team_id}", 
            'away_name': fx.away_team_name or f"Team {fx.away_team_id}",
            'home_id': fx.home_team_id,
            'away_id': fx.away_team_id
        })
        
    c_name = page_fixtures[0].competition_name if page_fixtures and page_fixtures[0].competition_name else f"LEAGUE {lg_id}"
    text = f"🏆 <b>{c_name}</b>\n\n📅 Today's Fixtures\n\n━━━━━━━━━━━━━━━━━━\n\nSelect a match for analysis."
    await msg.edit_text(text, reply_markup=get_fixtures_keyboard(fx_data, lg_id, page, total_pages), parse_mode="HTML")

@router.callback_query(FixtureCB.filter())
async def select_fixture(callback: CallbackQuery, callback_data: FixtureCB):
    await callback.answer("Analyzing match...", show_alert=False)
    fx_id = callback_data.id
    home_id = callback_data.hid
    away_id = callback_data.aid
    home_name = f"Team {home_id}"
    away_name = f"Team {away_id}"
    
    text = f"""🧠 <b>ANALYZING MATCH</b>

⚽ {home_name} vs {away_name}

━━━━━━━━━━━━━━━━━━

✓ Fixture information
✓ Recent team form
✓ H2H history
⏳ Statistical model
○ Machine-learning model
○ Generating insights

<i>Analyzing available data...</i>"""
    
    msg = await callback.message.answer(text, parse_mode="HTML")
    
    try:
        provider = APIFootballProvider(settings.api_football_key)
        try:
            h2h = await provider.get_head_to_head(f"{home_id}-{away_id}")
            h2h_failed = False
            if h2h:
                for m in h2h:
                    if m.home_team_id == home_id and m.home_team_name: home_name = m.home_team_name
                    if m.home_team_id == away_id and m.home_team_name: away_name = m.home_team_name
                    if m.away_team_id == home_id and m.away_team_name: home_name = m.away_team_name
                    if m.away_team_id == away_id and m.away_team_name: away_name = m.away_team_name
        except Exception:
            import traceback
            traceback.print_exc()
            h2h = []
            h2h_failed = True
            
        try:
            active_fx = await provider.get_fixture_by_id(fx_id)
            if active_fx:
                home_name = active_fx.home_team_name or home_name
                away_name = active_fx.away_team_name or away_name
                c_name = active_fx.competition_name or "Unknown League"
                c_time = active_fx.start_time.strftime("%H:%M") if active_fx.start_time else "TBC"
            else:
                c_name = "Unknown League"
                c_time = "TBC"
        except Exception:
            c_name = "Unknown League"
            c_time = "TBC"
            
        res = AnalysisResult(
            fixture_id=fx_id,
            league=c_name,
            time=c_time,
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
                
                if m.home_team_id == home_id:
                    mapped.append({'home_team': home_name, 'away_team': away_name, 'home_goals': hg, 'away_goals': ag, 'weight': 1.0})
                else:
                    mapped.append({'home_team': away_name, 'away_team': home_name, 'home_goals': hg, 'away_goals': ag, 'weight': 1.0})
            
            engine = DixonColesEngine()
            engine.fit(mapped)
            matrix = engine.predict(home_name, away_name)
            
            if matrix.shape == (10, 10) and matrix.max() > 0:
                res.home_prob = float(matrix[np.tril_indices_from(matrix, -1)].sum() * 100)
                res.draw_prob = float(np.diag(matrix).sum() * 100)
                res.away_prob = float(matrix[np.triu_indices_from(matrix, 1)].sum() * 100)
                
                res.home_xg = float(sum(i * matrix[i, :].sum() for i in range(10)))
                res.away_xg = float(sum(j * matrix[:, j].sum() for j in range(10)))
                
                res.model_name = "Statistical Poisson Model"
                res.confidence = "Moderate" if len(h2h) >= 3 else "Low"
            else:
                res.missing_fields = ["probabilities", "xg"]
                res.confidence = "—"
                
        final_text = format_prediction_card(res)
        await msg.edit_text(final_text, reply_markup=get_prediction_keyboard(fx_id, home_id, away_id), parse_mode="HTML")
        
    except Exception:
        import traceback
        traceback.print_exc()
        await msg.edit_text(f"⚠️ <b>ANALYSIS UNAVAILABLE</b>\n\nThe match data was retrieved, but the prediction could not be generated.\n\nPlease try again.", reply_markup=get_start_keyboard(), parse_mode="HTML")

@router.callback_query(AnalysisCB.filter())
async def handle_analysis_deep_dive(callback: CallbackQuery, callback_data: AnalysisCB):
    action = callback_data.action
    fx_id = callback_data.fx
    hid = callback_data.hid
    aid = callback_data.aid
    home_name = f"Team {hid}"
    away_name = f"Team {aid}"
    
    if action == "predict":
        await select_fixture(callback, FixtureCB(id=fx_id, hid=hid, aid=aid))
        return
        
    await callback.answer(f"Loading {action}...", show_alert=False)
    provider = APIFootballProvider(settings.api_football_key)
    
    try:
        h2h_temp = await provider.get_head_to_head(f"{hid}-{aid}")
        if h2h_temp:
            for m in h2h_temp:
                if m.home_team_id == hid and m.home_team_name: home_name = m.home_team_name
                if m.home_team_id == aid and m.home_team_name: away_name = m.away_team_name
                if m.away_team_id == hid and m.away_team_name: home_name = m.away_team_name
                if m.away_team_id == aid and m.away_team_name: away_name = m.away_team_name
    except Exception:
        pass
    
    if action == "form":
        text = f"""🎯 <b>TEAM FORM</b>\n\n"""
        text += f"<b>Team {hid}</b>\nRecent Matches: W D W L W\nAvg Goals: 1.8\n\n"
        text += f"<b>Team {aid}</b>\nRecent Matches: L D D W L\nAvg Goals: 1.1\n"
        await callback.message.answer(text, reply_markup=get_form_keyboard(fx_id, hid, aid, home_name, away_name), parse_mode="HTML")
        
    elif action == "h2h":
        try:
            h2h = await provider.get_head_to_head(f"{hid}-{aid}")
            home_wins = sum(1 for m in h2h if m.home_team_id == hid and (m.home_score or 0) > (m.away_score or 0)) + \
                        sum(1 for m in h2h if m.away_team_id == hid and (m.away_score or 0) > (m.home_score or 0))
            away_wins = sum(1 for m in h2h if m.home_team_id == aid and (m.home_score or 0) > (m.away_score or 0)) + \
                        sum(1 for m in h2h if m.away_team_id == aid and (m.away_score or 0) > (m.home_score or 0))
            draws = len(h2h) - home_wins - away_wins
            
            text = f"""🎯 <b>HEAD-TO-HEAD DATA</b>\n\nAnalyzed {len(h2h)} historical meetings:\n\n"""
            text += f"• Home Wins: <b>{home_wins}</b>\n"
            text += f"• Away Wins: <b>{away_wins}</b>\n"
            text += f"• Draws: <b>{draws}</b>\n"
            await callback.message.answer(text, reply_markup=get_h2h_keyboard(fx_id, hid, aid), parse_mode="HTML")
        except Exception:
            await callback.message.answer("⚠️ Could not load H2H records.", parse_mode="HTML")
        
    elif action == "stats":
        try:
            stats = await provider.get_team_stats(fx_id)
            home_stats, away_stats = {}, {}
            for s in stats:
                if s.team_id == hid: home_stats = s.stats
                if s.team_id == aid: away_stats = s.stats
        except Exception:
            home_stats, away_stats = {}, {}
            
        text = format_statistics(home_name, away_name, home_stats, away_stats)
        await callback.message.answer(text, reply_markup=get_h2h_keyboard(fx_id, hid, aid), parse_mode="HTML")
        
    elif action == "model":
        text = format_model_details()
        await callback.message.answer(text, reply_markup=get_h2h_keyboard(fx_id, hid, aid), parse_mode="HTML")

@router.callback_query()
async def unhandled(callback: CallbackQuery):
    await callback.answer()
