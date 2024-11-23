from telegram import BotCommand,InlineKeyboardButton, InlineKeyboardMarkup, Update, error
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import importlib
from tg_bot import tg

class VisualizationTask:
    def __init__(self, name,**kwargs):
        self.name = name
        self.module_name = name
        self.class_name = name
        try:
            module = importlib.import_module(self.module_name)
            self.cls = getattr(module, self.class_name)
            print(f"Успешная загрузка класса {self.class_name} из модуля {self.module_name}")
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"Ошибка загрузки класса {self.class_name} из модуля {self.module_name}: {e}")
            self.cls = None


SCENE_DICT = {
    'Tunneling': VisualizationTask('Tunneling'),
    'Oscilator': VisualizationTask('Oscilator'),  
    'Sqeeze': VisualizationTask('Sqeeze'),  
}


async def setup_commands(application):
    commands = [
        BotCommand("start", "Запустить бота")
    ]
    await application.bot.set_my_commands(commands)

async def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Сгенерировать рендер видео", callback_data="render_menu")],
        [InlineKeyboardButton("Скопировать опрос", callback_data="copy_poll")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await edit_or_send_msg(update,context,"Выберите действие:", markup)
        
async def render_menu(update, context):
    keyboard = []
    for scene_key, scene_class in SCENE_DICT.items():
        print(f"Добавление кнопки для задачи: {scene_key}")
        keyboard.append([InlineKeyboardButton(scene_key, callback_data=scene_key)])
    keyboard.append([InlineKeyboardButton("Назад в главное меню", callback_data="main_menu")])
    markup = InlineKeyboardMarkup(keyboard)
    await edit_or_send_msg(update,context,"Выберите задачу для рендера:", markup)

async def show_parameter_options(update, context):
    keyboard1 = [
        [InlineKeyboardButton("Параметры по умолчанию", callback_data='default')],
        [InlineKeyboardButton("Видео из бэкапа", callback_data='backup')],
        [InlineKeyboardButton("Выбрать параметры", callback_data='custom')],
        [InlineKeyboardButton("Назад к выбору", callback_data='render_menu')]
    ]
    markup = InlineKeyboardMarkup(keyboard1)
    await edit_or_send_msg(update,context,'Выберите параметры для задачи:', markup)



async def render_scene(scene_class:VisualizationTask, params=None):
    scene = scene_class.cls(**params) if params else scene_class.cls()
    scene.render()
    name = scene.name
    bot = tg()
    await bot.video_async(name)

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
                    print(f"Ошибка в параметре: {arg}")
                    await update.message.reply_text(f"Ошибка в параметре: {arg}")
                    return
        context.user_data['awaiting_params'] = False
        print(f"Пользователь ввел параметры: {params}")
        await render_scene(context.user_data['scene_class'], params)



async def button(update, context):
    query = update.callback_query
    await query.answer()
    print(f"Получен callback_data: {query.data}")

    if query.data in SCENE_DICT.keys():
        context.user_data['selected_task'] = query.data
        context.user_data['scene_class'] = SCENE_DICT[query.data]
        await show_parameter_options(update, context)

    elif query.data == 'default' or query.data == 'custom' or query.data == 'backup':
        selected_task = context.user_data['selected_task']
        if query.data == 'default':
            try:
                await query.edit_message_text(text=f"Выбраны параметры по умолчанию для задачи {selected_task}. Запуск рендеринга...")
                await render_scene(context.user_data['scene_class'])
            except ValueError as e:
                print(f"Ошибка создания экземпляра класса: {e}")
                await query.edit_message_text(text=str(e))

        elif query.data == 'custom':
            await query.edit_message_text(text="Отправь параметры в формате param=value.")
            context.user_data['awaiting_params'] = True
        
        elif query.data == 'backup':
            try:
                text1 = f"Запуск видео из бэкапа для задачи: {selected_task}"
                print(text1)
                bot = tg()
                await query.edit_message_text(text=text1)
                await bot.video_async(selected_task)
            except ValueError as e:
                await query.edit_message_text(text=str(e))
    
    elif query.data == 'main_menu':
        print("Возвращение в главное меню.")
        await main_menu(update, context)
    elif query.data == 'render_menu':
        print("Render menu.")
        await render_menu(update, context)
    elif query.data == 'copy_poll':
        print("copy_menu")
        await handle_copypoll_command(update,context)




async def handle_copypoll_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt="Отправьте сообщение с опросом для копирования"
    await edit_or_send_msg(update,context,txt)

    context.user_data["awaiting_poll"] = True
    context.user_data["target_chat_id"] = update.effective_chat.id
  
async def copy_poll_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_message = update.message
    question = poll_message.poll.question
    options = [option.text for option in poll_message.poll.options]
    await context.bot.send_poll(
        chat_id=context.user_data["target_chat_id"],
        question=question,
        options=options,
        is_anonymous=poll_message.poll.is_anonymous,
        allows_multiple_answers=poll_message.poll.allows_multiple_answers
    )
async def look_for_polls(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_poll", False):
        return
    for message in update.message.message_id:  
        if message.poll:
            await copy_poll_message(update,context)
    
    context.user_data["awaiting_poll"] = False

async def edit_or_send_msg(update, context, msg_txt,markup=None):
    if update.message:
        try:
            if 'bot_message_id' in context.user_data:
                await update.message.edit_text(text=msg_txt)
                await update.message.edit_reply_markup(reply_markup=markup)
            else:
                sent_message = await update.message.reply_text(msg_txt, reply_markup=markup)
                context.user_data['bot_message_id'] = sent_message.message_id
        except error.BadRequest:
            sent_message = await update.message.reply_text(msg_txt, reply_markup=markup)
            context.user_data['bot_message_id'] = sent_message.message_id
    elif update.callback_query:
        sent_message = await update.callback_query.edit_message_text(msg_txt, reply_markup=markup)
        context.user_data['bot_message_id'] = sent_message.message_id


def main():
    import asyncio
    bot = tg()
    print("Starting")
    token, _ = bot.get_token()

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", main_menu))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, custom_params))
    
    application.add_handler(CommandHandler("copypoll", handle_copypoll_command))
    application.add_handler(MessageHandler(filters.POLL, copy_poll_message))
    application.run_polling()
    asyncio.run(setup_commands(application))



if __name__ == '__main__':
    main()