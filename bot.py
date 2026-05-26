import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes

TOKEN = "8656424989:AAFTRBWft7tYargATcd8R7Nq0ak7RzP042M"
ADMIN_ID = 362693143
CHANNEL_ID = "@OVWedding"

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💍 Привіт! Надсилай фото або відео з весілля — "
        "вони анонімно з'являться в нашому каналі 📸\n\n"
        "Можна надсилати кілька фото одразу!"
    )

async def receive_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Опублікувати", callback_data="pub"),
            InlineKeyboardButton("❌ Відхилити", callback_data="del")
        ]
    ])
    try:
        if msg.photo:
            await context.bot.send_photo(
                chat_id=ADMIN_ID,
                photo=msg.photo[-1].file_id,
                caption="📸 Нове фото від гостя. Публікувати анонімно?",
                reply_markup=keyboard
            )
        elif msg.video:
            await context.bot.send_video(
                chat_id=ADMIN_ID,
                video=msg.video.file_id,
                caption="🎥 Нове відео від гостя. Публікувати анонімно?",
                reply_markup=keyboard
            )
        elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("image"):
            await context.bot.send_document(
                chat_id=ADMIN_ID,
                document=msg.document.file_id,
                caption="🖼 Нове зображення від гостя. Публікувати анонімно?",
                reply_markup=keyboard
            )
        else:
            await msg.reply_text("⚠️ Надсилай тільки фото або відео, будь ласка.")
            return
        await msg.reply_text("✅ Отримали! Скоро з'явиться в каналі 💍")
    except Exception as e:
        logging.error(f"Помилка при отриманні медіа: {e}")
        await msg.reply_text("❌ Щось пішло не так. Спробуй ще раз.")

async def handle_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data
    msg = query.message
    try:
        if action == "pub":
            if msg.photo:
                await context.bot.send_photo(chat_id=CHANNEL_ID, photo=msg.photo[-1].file_id, caption="📸")
            elif msg.video:
                await context.bot.send_video(chat_id=CHANNEL_ID, video=msg.video.file_id, caption="🎥")
            elif msg.document:
                await context.bot.send_document(chat_id=CHANNEL_ID, document=msg.document.file_id, caption="📸")
            await query.edit_message_caption("✅ Опубліковано в каналі")
        elif action == "del":
            await query.edit_message_caption("❌ Відхилено")
    except Exception as e:
        logging.error(f"Помилка при публікації: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, receive_media))
app.add_handler(CallbackQueryHandler(handle_decision))

print("Бот запущено ✅")
app.run_polling()
