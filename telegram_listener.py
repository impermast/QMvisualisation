from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

import traceback
from Tunneling import Tunneling3D
from tg_bot import tg

async def start(update, context):
    scene = Tunneling3D()
    default_params = scene.get_default_params()
    params_message = "Дефолтные параметры задачи:\n"
    for key, value in default_params.items():
        params_message += f"{key}={value}\n"
    await update.message.reply_text(params_message)
    
    keyboard1 = [
        [InlineKeyboardButton("Tunneling3D", callback_data='Tunneling3D')],
        [InlineKeyboardButton("Oscillator2D", callback_data='Oscillator2D')],
        [InlineKeyboardButton("Squeeze2D", callback_data='Squeeze2D')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard1)
    await update.message.reply_text('Привет! Выберите задачу для рендеринга:', reply_markup=reply_markup)


# Обработка выбора параметров
async def button(update, context):
    query = update.callback_query
    await query.answer()

    # Сохраняем выбор задачи
    if query.data in ['Tunneling3D', 'Oscillator2D', 'Squeeze2D']:
        context.user_data['selected_task'] = query.data
        await query.edit_message_text(text=f"Вы выбрали задачу: {query.data}")
        await show_parameter_options(update, context)

    elif query.data == 'default':
        selected_task = context.user_data.get('selected_task')
        if selected_task:
            await query.edit_message_text(text=f"Выбраны параметры по умолчанию для задачи {selected_task}. Запуск рендеринга...")
            scene_class = globals()[selected_task]  # Получаем класс по имени
            scene = scene_class()  # Создаем объект задачи
            default_params = scene.get_default_params()
            await render_scene(query, default_params)  # Запуск рендеринга с дефолтными параметрами

    elif query.data == 'custom':
        await query.edit_message_text(text="Отправь параметры в формате param=value.")
        context.user_data['awaiting_params'] = True
    
    elif query.data == 'backup':
        await send_video(query, context)

# Шаг 3: Показ параметров задачи
async def show_parameter_options(update, context):
    keyboard = [
        [InlineKeyboardButton("Параметры по умолчанию", callback_data='default')],
        [InlineKeyboardButton("Видео из бэкапа", callback_data='backup')],
        [InlineKeyboardButton("Выбрать параметры", callback_data='custom')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.reply_text('Выберите параметры для задачи:', reply_markup=reply_markup)


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
    try:
        await bot.video_async(name)
    except Exception as e:
        error_message = traceback.format_exc()
        bot.notify(message=f"Ошибка при рендере сцены: {str(e)}\n{error_message}")
    

async def render_scene(query, params):
    selected_task = query.message.chat_data['selected_task']
    scene_class = globals()[selected_task]
    scene = scene_class(**params)
    scene.render()
    name = scene.class_name
    bot = tg()
    await bot.video_async(name)
    
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
