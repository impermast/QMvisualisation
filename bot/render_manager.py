# render_manager.py
from .tg_bot import tg, edit_or_send_msg
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from animations import BoxExpansion, Tunneling, Oscilator, Squeeze, QuantumScattering

SCENE_DICT = {
    'Tunneling': Tunneling,
    'Oscilator': Oscilator,
    'Squeeze': Squeeze,
    'BoxExpansion': BoxExpansion,
    'QuantumScattering': QuantumScattering,
}

async def render_menu(update, context):
    keyboard = []
    for scene_key in SCENE_DICT.keys():
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

async def render_scene(scene_class, params=None):
    scene = scene_class(**params) if params else scene_class()
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
                        if '.' in value:
                            params[key] = float(value)
                        else:
                            params[key] = int(value)
                    except ValueError:
                        if value.lower() == 'true':
                            params[key] = True
                        elif value.lower() == 'false':
                            params[key] = False
                        else:
                            params[key] = value
                except ValueError:
                    print(f"Ошибка в параметре: {arg}")
                    await update.message.reply_text(f"Ошибка в параметре: {arg}")
                    return
        context.user_data['awaiting_params'] = False
        print(f"Пользователь ввел параметры: {params}")
        await render_scene(context.user_data['scene_class'], params)