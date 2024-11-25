

from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from tg_bot import tg


from render_manager import *
from poll_manager import *


async def setup_commands(application):
    commands = [
        BotCommand("start", "Запустить бота"),
        BotCommand("copypoll", "Копировать опрос"),
        BotCommand("savepolls", "Сохранить группу"),
    ]
    await application.bot.set_my_commands(commands)

async def main_menu(update, context):
    keyboard = [
        [InlineKeyboardButton("Сгенерировать рендер видео", callback_data="render_menu")],
        [InlineKeyboardButton("Работа с опросами", callback_data="copy_poll")],
        [InlineKeyboardButton("Показать сохраненные опросы", callback_data="show_polls")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await edit_or_send_msg(update,context,"Выберите действие:", markup)

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
    elif query.data == 'show_polls':
        print("show_polls")
        await show_polls(update,context)
    if query.data.startswith("print_group"):
        group_name = query.data[len("print_group_"):]
        await print_polls(update,context,group_name)



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

    application.add_handler(CommandHandler("savepolls", save_poll_group))
    
    application.run_polling()
    asyncio.run(setup_commands(application))



if __name__ == '__main__':
    main()
    