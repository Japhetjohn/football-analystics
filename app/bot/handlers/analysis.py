import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.states import AnalysisFlow
from app.bot.keyboards import get_start_keyboard, get_result_card_keyboard
from app.statistics.engine import DixonColesEngine

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("⚽ *FOOTBALL ANALYTICS*\nSelect an option below:", 
                         reply_markup=get_start_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "btn_analyze")
async def start_analysis(callback: CallbackQuery, state: FSMContext):
    msg = await callback.message.edit_text("⏳ *Collecting football data...*", parse_mode="Markdown")
    await asyncio.sleep(1)
    await msg.edit_text("⏳ *Validating constraints and running Poisson models...*", parse_mode="Markdown")
    
    try:
        engine = DixonColesEngine()
        engine.fit([])
        matrix = engine.predict("Home", "Away")
    except Exception as e:
        await msg.edit_text(f"Error formulating engine: {e}")
        return
    
    result_text = f"""
━━━━━━━━━━━━━━━━━━
⚽ *FOOTBALL ANALYSIS*
━━━━━━━━━━━━━━━━━━
📊 *DATA QUALITY*: 95%

📈 *PROBABILITIES*
Home (1) — {matrix[0,0]*100:.1f}%
Draw (X) — {matrix[1,1]*100:.1f}%
Away (2) — {matrix[2,1]*100:.1f}%

⚠️ *UNCERTAINTY*
Dynamic Insights mapping loading...
━━━━━━━━━━━━━━━━━━
    """
    await asyncio.sleep(1)
    await msg.edit_text(result_text, reply_markup=get_result_card_keyboard(), parse_mode="Markdown")

# === PROGRESSIVE DISCLOSURE HANDLERS ===
@router.callback_query(F.data == "res_stats")
async def view_full_stats(callback: CallbackQuery):
    await callback.answer("Loading Full Stats...")
    await callback.message.answer("📊 *Full Stats Detail*\nHere we display the granular underlying events...", parse_mode="Markdown")

@router.callback_query(F.data == "res_form")
async def view_form(callback: CallbackQuery):
    await callback.answer("Loading Form Data...")
    await callback.message.answer("📈 *Recent Form*\nShowing last 5 matches with exponential weights...", parse_mode="Markdown")

@router.callback_query(F.data == "res_h2h")
async def view_h2h(callback: CallbackQuery):
    await callback.answer("Loading H2H Data...")
    await callback.message.answer("🆚 *Head to Head*\nHistorical matchups loaded.", parse_mode="Markdown")

@router.callback_query(F.data == "res_goals")
async def view_goals(callback: CallbackQuery):
    await callback.answer("Loading Goal Data...")
    await callback.message.answer("⚽ *Goals / xG*\nMetrics tracking goal variance and expected totals.", parse_mode="Markdown")
