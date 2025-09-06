# Этот файл предназначен для локального тестирования и рендеринга сцен.
# Его можно переименовать в, например, `render_local.py` для ясности.
# Он не является основной точкой входа для телеграм-бота.

from bot import tg
import traceback

# Импортируйте сцены, которые вы хотите протестировать
from animations import Tunneling, Squeeze, Oscilator


if __name__ == "__main__":
    # --- НАСТРОЙКИ ДЛЯ ЛОКАЛЬНОГО РЕНДЕРА ---
    
    # Выберите сцену для рендеринга
    # scene_to_render = Tunneling
    scene_to_render = Squeeze
    # scene_to_render = Oscilator
    
    # Укажите параметры для сцены
    params = {
        'whattime':1,
        'test_logic':False
    }

    # --- КОНЕЦ НАСТРОЕК ---

    print(f"Запуск рендеринга для сцены: {scene_to_render.__name__}")
    scene = scene_to_render(**params)
    bot = tg()
    try: 
        scene.render() 
        print(f"Рендеринг завершен. Видео сохранено в: media/videos/1080p60/{scene.name}.mp4")
        # bot.video(scene.name) # Раскомментируйте, если хотите отправить видео в телеграм после рендера
    except Exception as e:
        error_message = traceback.format_exc()
        # bot.notify(message=f"Ошибка при рендере сцены: {str(e)}\n{error_message}")
        print(f"{str(e)}\n{error_message}")
