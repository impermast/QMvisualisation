from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from Tunneling import Tunneling3D
from tg_bot import tg

async def start(update, context):
    scene = Tunneling3D()
    default_params = scene.get_default_params()
    params_message = "Дефолтные параметры задачи:\n"
    for key, value in default_params.items():
        params_message += f"{key}={value}\n"
    await update.message.reply_text(params_message)
    
    keyboard = [
        [InlineKeyboardButton("Параметры по умолчанию", callback_data='default')],
        [InlineKeyboardButton("Видео из бэкапа", callback_data='backup')],
        [InlineKeyboardButton("Выбрать параметры", callback_data='custom')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Привет! Выберите вариант:', reply_markup=reply_markup)


# Обработка выбора параметров
async def button(update, context):
    query = update.callback_query
    await query.answer()

    if query.data == 'default':
        await query.edit_message_text(text="Выбраны параметры по умолчанию. Запуск рендеринга...")
        params = {}  
        await render_scene(query, params)

    elif query.data == 'custom':
        await query.edit_message_text(text="Отправь параметры в формате param=value.")
        context.user_data['awaiting_params'] = True
    elif query.data == 'backup':
        await send_video(update,context)

async def custom_params(update, context):
    if context.user_data.get('awaiting_params'):
        params = {}
        if len(update.message.text.split()) > 0:
            for arg in update.message.text.split():
                try:
                    key, value = arg.split('=')
                    try:
                        params[key] = float(value)
                    except ValueError:
                        params[key] = value
                    
                except ValueError:
                    await update.message.reply_text(f"Ошибка в параметре: {arg}")
                    return
        context.user_data['awaiting_params'] = False
        await render_scene(update, params)

async def send_video(update,context):
    bot = tg()
    await bot.video_async()

async def render_scene(update, params):
    await update.message.reply_text("Запуск рендеринга...")
    scene = Tunneling3D(**params)
    scene.render()
    await update.message.reply_text("Рендеринг завершен.")
    bot = tg()
    await bot.video_async()
    
def main():
    bot = tg()
    token , _ = bot.get_token()
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("video", send_video))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, custom_params))


    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
