from telegram import InlineKeyboardButton, InlineKeyboardMarkup

UNCHECKED = "▫️"
CHECKED = "✅"


def build_keyboard(list_key: str, items: list[str]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(f"{UNCHECKED} {item}", callback_data=f"t:{list_key}:{i}")]
        for i, item in enumerate(items)
    ]
    return InlineKeyboardMarkup(buttons)


def toggle_keyboard(markup: InlineKeyboardMarkup, item_index: int) -> InlineKeyboardMarkup:
    rows = [list(row) for row in markup.inline_keyboard]
    btn = rows[item_index][0]
    text = btn.text
    if text.startswith(CHECKED):
        new_text = UNCHECKED + text[len(CHECKED):]
    else:
        new_text = CHECKED + text[len(UNCHECKED):]
    rows[item_index][0] = InlineKeyboardButton(new_text, callback_data=btn.callback_data)
    return InlineKeyboardMarkup(rows)
