from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.constants import MessageEntityType

# Ваш ID администратора
ADMIN_CHAT_ID = 6551226424  # Замените на ваш ID

# Словарь для хранения ID и сообщений от пользователей
user_messages = {}

# Обработка текстовых сообщений и пересылка их администратору
async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_message = update.message.text

    # Сохраняем ID и сообщение пользователя для ответа
    user_messages[user_id] = user_message

    # Пересылаем сообщение администратору
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"Сообщение от пользователя {user_id}:\n\n{user_message}"
    )

    # Подтверждаем пользователю, что сообщение отправлено администратору
    if user_id != ADMIN_CHAT_ID:
        await update.message.reply_text("Ваше сообщение отправлено администратору.")

# Обработка фото и пересылка администратору
async def forward_photo_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_photo = update.message.photo[-1].file_id  # Берем фото в наилучшем качестве

    user_messages[user_id] = "[Фото]"

    # Пересылаем фото администратору
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=user_photo,
        caption=f"Фото от пользователя {user_id}"
    )

# Обработка документов и пересылка администратору
async def forward_document_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_document = update.message.document.file_id

    user_messages[user_id] = "[Документ]"

    # Пересылаем документ администратору
    await context.bot.send_document(
        chat_id=ADMIN_CHAT_ID,
        document=user_document,
        caption=f"Документ от пользователя {user_id}"
    )

# Ответ админа пользователям (включая возможность отправки текста и медиафайлов)
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id == ADMIN_CHAT_ID:
        command_parts = update.message.text.split(maxsplit=2)
        
        if len(command_parts) < 3:
            await update.message.reply_text("Формат команды: /reply [user_id] [сообщение]")
            return

        _, user_id_str, reply_message = command_parts
        
        try:
            user_id = int(user_id_str)
            if user_id in user_messages:
                await context.bot.send_message(chat_id=user_id, text=reply_message)
                await update.message.reply_text(f"Ответ отправлен пользователю {user_id}.")
            else:
                await update.message.reply_text(f"Пользователь с ID {user_id} не найден.")
        except ValueError:
            await update.message.reply_text("Некорректный ID пользователя.")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Напишите ваше сообщение, и администратор скоро ответит.")

if __name__ == "__main__":
    app = Application.builder().token("7928801459:AAE1273ZPWwT_3rXXLnjZCKpQ1uzdd27kZI").build()

    # Обработчики команд и сообщений
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))
    app.add_handler(CommandHandler("reply", reply_to_user))
    
    # Обработчики для фото и документов
    app.add_handler(MessageHandler(filters.PHOTO, forward_photo_to_admin))
    app.add_handler(MessageHandler(filters.Document.ALL, forward_document_to_admin))

    # Запуск бота
    app.run_polling()