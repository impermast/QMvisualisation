import telegram
import json
import asyncio,os

async def send_telegram_message(message, token, chat_id):
    """Отправка сообщения в Telegram."""
    bot = telegram.Bot(token=token)
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except telegram.error.TelegramError as e:
        print(f"Ошибка при отправке сообщения: {e}")

async def test_telegram_connection():
    """Тестовая отправка сообщения."""
    token, chat_id = load_telegram_config()
    if token is None or chat_id is None:
        print("Не удалось загрузить конфигурацию Telegram.")
        return

    print("Запускаю функцию")
    await send_telegram_message("Тестовое сообщение", token, chat_id)
    print("Тестовое сообщение отправлено")

# Асинхронная функция для отправки видео в Telegram
async def send_telegram_video(video_path, token, chat_id):
    bot = telegram.Bot(token=token)
    try:
        with open(video_path, 'rb') as video_file:
            await bot.send_video(chat_id=chat_id, video=video_file)
    except telegram.error.TelegramError as e:
        print(f"Ошибка при отправке видео: {e}")
    except FileNotFoundError:
        print(f"Видео не найдено по пути: {video_path}")


# Функция для получения токена и ID чата из конфигурации
def load_telegram_config(config_path="config.json"):
    """Загружает конфигурацию из файла config.json"""
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        return config.get("telegram_token"), config.get("telegram_chat_id")
    except FileNotFoundError:
        print(f"Ошибка: файл конфигурации '{config_path}' не найден.")
        return None, None
    except json.JSONDecodeError:
        print(f"Ошибка при разборе конфигурационного файла '{config_path}'.")
        return None, None

class tg:
    def __init__(self):
        self.token, self.chat_id = load_telegram_config()
    
    def get_token(self):
        return self.token, self.chat_id

    def notify(self, message="Рендеринг завершен."):
        """Отправить сообщение в Telegram после завершения рендеринга.""" 
        if self.token and self.chat_id:
            asyncio.run(send_telegram_message(message, self.token, self.chat_id))
        
    def video(self, path="media/videos/1080p60/Tunneling3D.mp4"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        abs_path = os.path.join(current_dir,path)
        if self.token and self.chat_id:
            asyncio.run(send_telegram_video(abs_path, self.token, self.chat_id))
 


# Вызывайте тестовую функцию через asyncio.run
if __name__ == "__tg_bot__":
    asyncio.run(test_telegram_connection())
