# handlers.py
import importlib
from tg_bot import tg, edit_or_send_msg
from telegram import BotCommand,InlineKeyboardButton, InlineKeyboardMarkup, Update, error




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



