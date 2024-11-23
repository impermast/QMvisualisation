# Запуск анимации

from tg_bot import tg
import traceback
from Tunneling import Tunneling
from Sqeeze import Sqeeze
from Oscilator import Oscilator



if __name__ == "__main__":
    params = {
        'whattime':1,
        'test_logic':False
    }
    scene = Sqeeze(**params)
    name = scene.class_name
    bot = tg()
    try: 
        scene.render() 
        print("Rendering over\nSending to tg\n")
        bot.video(name)
    except Exception as e:
        error_message = traceback.format_exc()
        bot.notify(message=f"Ошибка при рендере сцены: {str(e)}\n{error_message}")
        print(f"{str(e)}\n{error_message}")


