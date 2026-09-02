from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    """Main Menu Keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Analyze Match", callback_data="btn_analyze")],
        [InlineKeyboardButton(text="ℹ️ About", callback_data="btn_about")]
    ])

def get_result_card_keyboard() -> InlineKeyboardMarkup:
    """Progressive disclosure sub-views"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Full Stats", callback_data="res_stats"),
            InlineKeyboardButton(text="📈 Form", callback_data="res_form")
        ],
        [
            InlineKeyboardButton(text="🆚 H2H", callback_data="res_h2h"),
            InlineKeyboardButton(text="⚽ Goals", callback_data="res_goals")
        ]
    ])
