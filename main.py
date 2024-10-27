# Запуск анимации

from tg_bot import tg
from Tunneling import Tunneling3D
from squeezestate import Sqeeze2D


if __name__ == "__main__":
    params = {
        'whattime':0.1,
        'test_logic':False
    }
    scene = Sqeeze2D(**params)
    scene.render()
    print("Rendering over\nSending to tg\n")
    bot = tg()
    bot.video()
