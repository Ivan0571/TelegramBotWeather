from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import logging
import requests

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = '7676076143:AAHSuExd5eMUtUwyAA364jNOH7s3eRBSBxA'

OPENWEATHER_API_KEY = "9d748340f0e289578a099c0504eea5f4"

CITY_INPUT = 1

async def start(update: Update, contex):
    user = update.effective_user
    await update.message.reply_text(f"Привет, {user.first_name}! Я многофункциональный бот.\n"
                                    "/start - Начать\n"
        "/help - Помощь\n"
        "/weather - Узнать погоду\n"
        "/info - Информация о вас\n"
        "/cancel - Отменить текущее действие")

async def help_command(update: Update, contex):
    await update.message.reply_text("Список доступных команд:\n"
                                    "/start - Начать\n"
                                    "/help - Помощь\n"
                                    "/info - Информация о вас\n"
                                    "/weather - Узнать погоду\n"
                                    "/cancel - Отменить текущее действие")

async def info_command(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(f"Ваше имя: {user.first_name}\n"
                                    f"Ваш username: {user.username}\n"
                                    f"Ваш ID: {user.id}")


async def weather_start(update: Update, contex):
    await update.message.reply_text("Введите название города:")
    return CITY_INPUT

async def get_weather(update: Update, contex):
    city = update.message.text
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()

        if data["cod"] == 200:
            weather = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            await update.message.reply_text(f"Текущая погода в {city}:\n"
                                            f"{weather.capitalize()}, температура: {temperature}°C")
        else:
            await update.message.reply_text(f"Город {city} не найден или данные недоступны.")
    except Exception as e:
        logger.error(f"Ошибка при получении погоды: {e}")
        await update.message.reply_text("Произошла ошибка при получении погоды.")
    return ConversationHandler.END

async def cancel(update: Update, contex):
    await update.message.reply_text("Диалог отменен.")
    return ConversationHandler.END

async def handler_photo(update: Update, contex):
    await update.message.reply_text("Вы отправили фото!")

async def log_message(update: Update, contex):
    logger.info(f"Пользователь {update.effective_user.id} сказал: {update.message.text}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("weather", weather_start)],
        states={
            CITY_INPUT: {MessageHandler(filters.TEXT & ~filters.COMMAND, get_weather)}
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(MessageHandler(filters.PHOTO, handler_photo))

    application.add_handler(MessageHandler(filters.ALL, log_message), group=1)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()