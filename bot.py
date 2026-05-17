# -*- coding: utf-8 -*-
import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ConversationHandler, filters, ContextTypes
)
from telegram.error import NetworkError, TimedOut

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ─── НАСТРОЙКИ ────────────────────────────────────────────────
TOKEN           = "8995561685:AAHUNS2d5mpo8508Rm_euQ2_sM_UanUcrA0"
MANAGER_CHAT_ID = 938980190
# ──────────────────────────────────────────────────────────────

CITY, CAR, NAME, PHONE = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет!\n\n"
        "Я помогу оформить заявку на перевозку автомобиля из Владивостока.\n\n"
        "В какой *город* доставляем? 🗺",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    return CITY


async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["city"] = update.message.text.strip()
    await update.message.reply_text(
        f"✅ Доставим в *{context.user_data['city']}*!\n\n"
        "Укажите марку, модель и год автомобиля 🚗\n"
        "_Пример: Toyota Camry 2021_",
        parse_mode="Markdown"
    )
    return CAR


async def get_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["car"] = update.message.text.strip()
    await update.message.reply_text(
        "Как вас зовут? 👤"
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text.strip()
    await update.message.reply_text(
        "И последнее — номер телефона для связи 📞\n"
        "_Пример: +7 900 000-00-00_",
        parse_mode="Markdown"
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text.strip()
    d = context.user_data
    user = update.message.from_user

    # ── Подтверждение клиенту ──
    await update.message.reply_text(
        "🎉 *Заявка принята!*\n\n"
        f"📍 Город доставки: {d['city']}\n"
        f"🚗 Автомобиль: {d['car']}\n"
        f"👤 Имя: {d['name']}\n"
        f"📞 Телефон: {d['phone']}\n\n"
        "Менеджер свяжется с вами в течение *15 минут*.",
        parse_mode="Markdown"
    )

    # ── Уведомление менеджеру ──
    username = f"@{user.username}" if user.username else f"tg://user?id={user.id}"
    await context.bot.send_message(
        chat_id=MANAGER_CHAT_ID,
        text=(
            "🔔 *НОВАЯ ЗАЯВКА — ДальАвто*\n\n"
            f"📍 Город: {d['city']}\n"
            f"🚗 Авто: {d['car']}\n"
            f"👤 Имя: {d['name']}\n"
            f"📞 Телефон: {d['phone']}\n"
            f"✈️ Клиент: {username}"
        ),
        parse_mode="Markdown"
    )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отменено. Напишите /start чтобы начать заново.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, (NetworkError, TimedOut)):
        logging.warning("Network error, ignoring: %s", context.error)
        if isinstance(update, Update) and update.message:
            try:
                await update.message.reply_text(
                    "Сеть пропала на секунду. Попробуйте ещё раз или напишите /start."
                )
            except Exception:
                pass
    else:
        logging.error("Unexpected error: %s", context.error, exc_info=context.error)


def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CITY:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
            CAR:   [MessageHandler(filters.TEXT & ~filters.COMMAND, get_car)],
            NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_error_handler(error_handler)

    print("Bot started. Press Ctrl+C to stop.")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
