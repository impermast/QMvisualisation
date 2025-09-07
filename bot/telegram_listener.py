from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from .tg_bot import tg, edit_or_send_msg
from telegram import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
import os

from .poll_manager import handle_copypoll_command, copy_poll_message, save_poll_group, show_polls, cancel_copy, print_polls

from animations import BoxExpansion, Ladder, Oscilator, ProbabilityCurrent, QuantumScattering, Squeeze, Tunneling

ANIMATION_CLASSES = {
    'BoxExpansion': BoxExpansion,
    'Ladder': Ladder,
    'Oscilator': Oscilator,
    'ProbabilityCurrent': ProbabilityCurrent,
    'QuantumScattering': QuantumScattering,
    'Squeeze': Squeeze,
    'Tunneling': Tunneling,
}

class TelegramListener:
    def __init__(self):
        self.bot_instance = tg()
        self.application = None
        self.video_path = "c:\\progs\\QMvisualisation\\media\\videos\\1080p60\\"

    async def setup_commands(self, application):
        commands = [
            BotCommand("start", "Запустить бота"),
            BotCommand("copypoll", "Копировать опрос"),
            BotCommand("savepolls", "Сохранить группу"),
        ]
        await application.bot.set_my_commands(commands)

    async def main_menu(self, update, context):
        keyboard = [
            [InlineKeyboardButton("Работа с опросами", callback_data="copy_poll")],
            [InlineKeyboardButton("Показать сохраненные опросы", callback_data="show_polls")],
            [InlineKeyboardButton("Показать информацию об анимациях", callback_data="animation_info_menu")],
            [InlineKeyboardButton("Видео из бэкапа", callback_data="backup_video")],
            [InlineKeyboardButton("Квантовые концепции", callback_data="quantum_concepts")],
            [InlineKeyboardButton("Рекомендуемая литература", callback_data="literature_list")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await edit_or_send_msg(update, context, "Выберите действие:", markup)

    async def animation_info_menu(self, update, context):
        keyboard = []
        for anim_name, anim_class in ANIMATION_CLASSES.items():
            keyboard.append([InlineKeyboardButton(anim_name, callback_data=f"anim_info_{anim_name}")])
        keyboard.append([InlineKeyboardButton("Назад в главное меню", callback_data="main_menu")])
        markup = InlineKeyboardMarkup(keyboard)
        await edit_or_send_msg(update, context, "Выберите анимацию для просмотра информации:", markup)

    async def show_animation_details(self, update, context, anim_name):
        anim_class = ANIMATION_CLASSES.get(anim_name)
        if anim_class:
            info = anim_class.get_info()
            message_text = f"**{info['name']}**\n\n{info['description']}"
            keyboard = [[InlineKeyboardButton("Назад к списку анимаций", callback_data="animation_info_menu")],
                        [InlineKeyboardButton("Назад в главное меню", callback_data="main_menu")]]
            markup = InlineKeyboardMarkup(keyboard)
            await edit_or_send_msg(update, context, message_text, markup)
        else:
            await edit_or_send_msg(update, context, "Информация об этой анимации не найдена.")

    async def handle_backup_video(self, update, context):
        video_files = []
        try:
            for file_name in os.listdir(self.video_path):
                if file_name.endswith(".mp4"):
                    video_files.append(file_name.replace(".mp4", ""))
        except FileNotFoundError:
            await edit_or_send_msg(update, context, "Папка с видео не найдена.")
            return

        if not video_files:
            await edit_or_send_msg(update, context, "В папке с видео нет файлов.")
            return

        keyboard = []
        for video_name in video_files:
            keyboard.append([InlineKeyboardButton(video_name, callback_data=f"select_video_{video_name}")])
        keyboard.append([InlineKeyboardButton("Назад в главное меню", callback_data="main_menu")])
        markup = InlineKeyboardMarkup(keyboard)
        await edit_or_send_msg(update, context, "Выберите видео для просмотра:", markup)

    async def send_selected_video(self, update, context, video_name):
        await edit_or_send_msg(update, context, f"Запуск видео: {video_name}...")
        await self.bot_instance.video_async(video_name)

    async def show_literature_list(self, update, context):
        try:
            with open("c:\\progs\\QMvisualisation\\media\\literature.txt", "r", encoding="utf-8") as f:
                literature_text = f.read()
        except FileNotFoundError:
            literature_text = "Файл с литературой не найден."
        
        keyboard = [[InlineKeyboardButton("Назад в главное меню", callback_data="main_menu")]]
        markup = InlineKeyboardMarkup(keyboard)
        await edit_or_send_msg(update, context, literature_text, markup)

    async def button(self, update, context):
        query = update.callback_query
        await query.answer()
        print(f"Получен callback_data: {query.data}")

        if query.data == 'main_menu':
            print("Возвращение в главное меню.")
            await self.main_menu(update, context)
        elif query.data == 'animation_info_menu':
            print("Animation Info Menu.")
            await self.animation_info_menu(update, context)
        elif query.data.startswith("anim_info_"):
            anim_name = query.data[len("anim_info_"):]
            await self.show_animation_details(update, context, anim_name)
        elif query.data == 'backup_video':
            print("Backup Video.")
            await self.handle_backup_video(update, context)
        elif query.data.startswith("select_video_"):
            video_name = query.data[len("select_video_"):]
            await self.send_selected_video(update, context, video_name)
        elif query.data == 'literature_list':
            print("Literature List.")
            await self.show_literature_list(update, context)
        elif query.data == 'copy_poll':
            print("copy_menu")
            await handle_copypoll_command(update, context)
        elif query.data == 'show_polls':
            print("show_polls")
            await show_polls(update, context)
        elif query.data == 'cancel_copy':
            print("Canceling poll copy.")
            await cancel_copy(update, context)
        if query.data.startswith("print_group"):
            group_name = query.data[len("print_group_"):]
            await print_polls(update, context, group_name)

    def run(self):
        print("Starting TelegramListener")
        token, _ = self.bot_instance.get_token()

        self.application = Application.builder().token(token).post_init(self.setup_commands).build()

        self.application.add_handler(CommandHandler("start", self.main_menu))
        self.application.add_handler(CallbackQueryHandler(self.button))
        
        self.application.add_handler(CommandHandler("copypoll", handle_copypoll_command))
        self.application.add_handler(MessageHandler(filters.POLL, copy_poll_message))
        self.application.add_handler(CommandHandler("savepolls", save_poll_group))
        
        return self.application

if __name__ == '__main__':
    listener = TelegramListener()
    application = listener.run()
    application.run_polling()