# poll_manager.py
import os
import json

from tg_bot import edit_or_send_msg
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton


POLL_GROUPS_DIR = "poll_groups"

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
    polls = context.user_data.get("polls", [])
    success, message = poll_manager.save_group(group_name, polls)
    if success:
        await edit_or_send_msg(update, context, 
                               f"Группа опросов '{group_name}' успешно сохранена.")
        context.user_data["polls"] = []  # Очищаем временное хранилище опросов
    else:
        await edit_or_send_msg(update, context,
                            f"Ошибка при сохранении группы: {message}")


async def handle_copypoll_command(update: Update, context):
    txt="Отправьте сообщение с опросом для копирования"
    await edit_or_send_msg(update,context,txt)

    context.user_data["awaiting_poll"] = True
    context.user_data["target_chat_id"] = update.effective_chat.id
  
async def copy_poll_message(update: Update, context):
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
    

async def look_for_polls(update: Update, context):
    if not context.user_data.get("awaiting_poll", False):
        return
    for message in update.message.message_id:  
        if message.poll:
            await copy_poll_message(update,context)
    await save_poll_group(update,context)
    
    context.user_data["awaiting_poll"] = False

async def show_polls(update: Update, context):
    group_files = poll_manager.list_groups()
    if not group_files:
        await edit_or_send_msg(update,context,"Нет сохранённых групп.")
        return

    keyboard = [[InlineKeyboardButton(group_name, callback_data=f"print_group_{group_name}")] for group_name in group_files]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await edit_or_send_msg(update, context, 
                "Выберите группу опросов:", reply_markup)

async def print_polls(update, context, group_name):
    loaded_polls, msg = poll_manager.load_group(group_name)
    for poll1 in loaded_polls["polls"]:
        await context.bot.send_poll(
            chat_id = update.effective_chat.id,
            question=poll1["question"],
            options=poll1["options"],
            is_anonymous=poll1["is_anonymous"],
            allows_multiple_answers=poll1["allows_multiple_answers"]
        )
    await edit_or_send_msg(update,context,msg)



if __name__ == "__main__":
    data, mes = poll_manager.load_group("testpoll")
    print(data["polls"])
    print(data["polls"][1]["question"])
    data_dict = {}
    for item in data:
        if isinstance(item, dict):  # Убедимся, что элемент — это словарь
          data_dict.update(item)
