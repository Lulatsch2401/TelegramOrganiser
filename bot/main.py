import logging

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from . import lists
from .config import load_config
from .keyboards import build_keyboard, toggle_keyboard

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keywords = lists.get_all_keywords()
    kw_str = ", ".join(f"`{k}`" for k in keywords)
    await update.message.reply_text(
        f"👋 Hallo! Ich bin dein Packlisten-Bot.\n\n"
        f"Gib einfach ein Stichwort ein, z. B. `schwimmen`, und ich zeige dir die Checkliste.\n\n"
        f"Verfügbare Listen: {kw_str}\n\n"
        f"/listen – alle Stichwörter\n"
        f"/reload – Listen neu laden",
        parse_mode="Markdown",
    )


async def list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keywords = lists.get_all_keywords()
    kw_str = "\n".join(f"• `{k}`" for k in keywords)
    await update.message.reply_text(
        f"📋 Verfügbare Packlisten:\n\n{kw_str}",
        parse_mode="Markdown",
    )


async def reload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info("User %s (%d) requested reload", user.username, user.id)
    try:
        count = lists.load_lists()
    except Exception as exc:
        logger.error("Failed to reload lists: %s", exc)
        await update.message.reply_text(f"❌ Fehler beim Laden: {exc}")
        return
    await update.message.reply_text(f"✅ {count} Listen neu geladen.")


async def keyword_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.strip()
    user = update.effective_user
    logger.info("User %s (%d) queried: %r", user.username, user.id, text)

    if text.lower() == "listen":
        await list_handler(update, context)
        return

    entry = lists.get_list(text)
    if entry:
        items = entry.get("items") or []
        if not items:
            await update.message.reply_text(f"📋 {entry['title']} — Liste ist leer.")
            return
        kb = build_keyboard(entry["key"], items)
        await update.message.reply_text(
            f"*{entry['title']}*",
            reply_markup=kb,
            parse_mode="Markdown",
        )
        return

    suggestion = lists.fuzzy_match(text)
    if suggestion:
        matched = lists.get_list(suggestion)
        hint = f"\n\nMeintest du *{matched['title']}*? Gib `{suggestion}` ein." if matched else ""
    else:
        hint = ""

    await update.message.reply_text(
        f"❓ Keine Liste für *{text}* gefunden.{hint}\n\n"
        f"Tippe /listen für alle verfügbaren Stichwörter.",
        parse_mode="Markdown",
    )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = query.from_user
    allowed_ids: set[int] = context.application.bot_data.get("allowed_user_ids", set())
    if user.id not in allowed_ids:
        await query.answer("⛔ Nicht berechtigt.")
        return

    data = query.data
    if not data.startswith("t:"):
        await query.answer()
        return

    _, list_key, idx_str = data.split(":", 2)
    item_index = int(idx_str)

    new_markup = toggle_keyboard(query.message.reply_markup, item_index)
    await query.answer()
    await query.edit_message_reply_markup(reply_markup=new_markup)


async def unauthorized_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    uid = user.id if user else -1
    logger.warning("Unauthorized access attempt by user %d", uid)
    if update.message:
        await update.message.reply_text("⛔ Du bist nicht berechtigt, diesen Bot zu nutzen.")


def main() -> None:
    load_dotenv()
    config = load_config()
    lists.load_lists()

    app = Application.builder().token(config.bot_token).build()
    app.bot_data["allowed_user_ids"] = set(config.allowed_user_ids)

    allowed = filters.User(user_id=config.allowed_user_ids)

    app.add_handler(CommandHandler("start", start_handler, filters=allowed))
    app.add_handler(CommandHandler("listen", list_handler, filters=allowed))
    app.add_handler(CommandHandler("reload", reload_handler, filters=allowed))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(allowed & filters.TEXT & ~filters.COMMAND, keyword_handler))
    app.add_handler(MessageHandler(~allowed & (filters.TEXT | filters.COMMAND), unauthorized_handler))

    logger.info("Bot starting with %d allowed user(s)", len(config.allowed_user_ids))
    app.run_polling()


if __name__ == "__main__":
    main()
