# poll_manager.py
import os
import json

from tg_bot import edit_or_send_msg
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton


POLL_GROUPS_DIR = os.path.join("bot", "poll_groups")

class PollManager:
    def __init__(self):
        if not os.path.exists(POLL_GROUPS_DIR):
            os.makedirs(POLL_GROUPS_DIR)

    def save_group(self, group_name, polls):
        group_file = os.path.join(POLL_GROUPS_DIR, f"{group_name}.json")
        if os.path.exists(group_file):
            return False, "Группа с таким именем уже существует."
        with open(group_file, "w") as file:
            json.dump({"group_name": group_name, "polls": polls}, file, ensure_ascii=False, indent=4)
        return True, "Группа успешно сохранена."

    def load_group(self, group_name):
        group_file = os.path.join(POLL_GROUPS_DIR, f"{group_name}.json")
        if not os.path.exists(group_file):
            return None, "Группа не найдена."
        with open(group_file, "r") as file:
            data = json.load(file)
        return data, "Группа загружена."

    def list_groups(self):
        return [f[:-5] for f in os.listdir(POLL_GROUPS_DIR) if f.endswith(".json")]



poll_manager = PollManager()

async def save_poll_group(update, context):
    group_name = update.message.text[len("/savepolls "):]
    if not group_name:
        await edit_or_send_msg(update, context, "Вы должны указать имя группы. Пример: /savepolls МояГруппа")
        return

    polls = context.user_data.get("polls", [])
    if not polls:
        await edit_or_send_msg(update, context, "Нет опросов для сохранения. Сначала скопируйте их с помощью /copypoll.")
        return

    success, message = poll_manager.save_group(group_name, polls)
    if success:
        await edit_or_send_msg(update, context, 
                               f"Группа опросов '{group_name}' успешно сохранена.")
        context.user_data["polls"] = []  # Очищаем временное хранилище опросов
        context.user_data["awaiting_poll"] = False # Завершаем режим копирования
    else:
        await edit_or_send_msg(update, context,
                            f"Ошибка при сохранении группы: {message}")


async def handle_copypoll_command(update: Update, context):
    txt="Вы в режиме копирования опросов.\n\nПересылайте сюда опросы, которые хотите добавить в группу. Когда закончите, нажмите кнопку ниже или используйте команду /savepolls, чтобы сохранить группу."
    keyboard = [[InlineKeyboardButton("Завершить и отменить", callback_data="cancel_copy")]]
    markup = InlineKeyboardMarkup(keyboard)
    await edit_or_send_msg(update,context,txt, markup=markup)

    context.user_data["awaiting_poll"] = True
    context.user_data["target_chat_id"] = update.effective_chat.id
  
async def copy_poll_message(update: Update, context):
    # Копируем опрос, только если бот находится в режиме ожидания
    if not context.user_data.get("awaiting_poll", False):
        return

    poll_message = update.message
    question = poll_message.poll.question
    options = [option.text for option in poll_message.poll.options]
    is_anonymous = poll_message.poll.is_anonymous
    allows_multiple_answers = poll_message.poll.allows_multiple_answers

    await context.bot.send_poll(
        chat_id=context.user_data["target_chat_id"],
        question=question,
        options=options,
        is_anonymous=poll_message.poll.is_anonymous,
        allows_multiple_answers=poll_message.poll.allows_multiple_answers
    )
    if "polls" not in context.user_data:
        context.user_data["polls"] = []
    context.user_data["polls"].append({
        "question": question,
        "options": options,
        "is_anonymous": is_anonymous,
        "allows_multiple_answers": allows_multiple_answers
    })
    
async def cancel_copy(update: Update, context):
    """Отменяет режим копирования опросов."""
    context.user_data["awaiting_poll"] = False
    copied_count = len(context.user_data.get("polls", []))
    context.user_data["polls"] = []
    await edit_or_send_msg(update, context, f"Режим копирования отменен. Временный список из {copied_count} опросов очищен.")
    # Чтобы вернуть пользователя в главное меню, можно раскомментировать:
    # from telegram_listener import main_menu
    # await main_menu(update, context)

async def show_polls(update: Update, context):
    group_files = poll_manager.list_groups()
    if not group_files:
        await edit_or_send_msg(update,context,"Нет сохранённых групп.")
        return

    keyboard = [
        [InlineKeyboardButton(group_name, callback_data=f"print_group_{group_name}")] for group_name in group_files
    ]
    keyboard.append([InlineKeyboardButton("Назад в главное меню", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await edit_or_send_msg(update, context, 
                "Выберите группу опросов:", reply_markup)

async def print_polls(update, context, group_name):
    loaded_polls, msg = poll_manager.load_group(group_name)
    if not loaded_polls:
        await edit_or_send_msg(update, context, msg)
        return

    for poll1 in loaded_polls["polls"]:
        await context.bot.send_poll(
            chat_id = update.effective_chat.id,
            question=poll1["question"],
            options=poll1["options"],
            is_anonymous=poll1["is_anonymous"],
            allows_multiple_answers=poll1["allows_multiple_answers"]
        )
    
    # После отправки опросов, можно показать меню снова или просто уведомить
    await edit_or_send_msg(update, context, f"Опросы из группы '{group_name}' отправлены.")



if __name__ == "__main__":
    # Это пример использования PollManager для локального тестирования.
    
    # 1. Создаем экземпляр менеджера
    pm = PollManager()
    test_group_name = "my_test_group"
    test_group_file = os.path.join(POLL_GROUPS_DIR, f"{test_group_name}.json")

    # Убедимся, что тестовый файл не существует перед началом
    if os.path.exists(test_group_file):
        os.remove(test_group_file)

    # 2. Определяем тестовые данные для опросов
    sample_polls = [
        {
            "question": "Какой ваш любимый цвет?",
            "options": ["Красный", "Зеленый", "Синий"],
            "is_anonymous": True,
            "allows_multiple_answers": False
        }
    ]

    # 3. Сохраняем группу
    print(f"Сохранение группы '{test_group_name}'...")
    success, message = pm.save_group(test_group_name, sample_polls)
    print(f"Результат: {success}, {message}")
    assert success is True

    # 4. Загружаем группу и проверяем содержимое
    print(f"\nЗагрузка группы '{test_group_name}'...")
    loaded_data, message = pm.load_group(test_group_name)
    print(f"Результат: {message}")
    assert loaded_data is not None
    assert loaded_data["polls"] == sample_polls
    print("Содержимое группы успешно проверено.")

    # 5. Очистка: удаляем тестовый файл
    if os.path.exists(test_group_file):
        os.remove(test_group_file)
    print(f"\nТестовый файл '{test_group_file}' удален. Тестирование завершено.")
