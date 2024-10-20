# Запуск анимации

from tg_bot import tg
from Tunneling import Tunneling3D

if __name__ == "__main__":
    params = {
        'whattime':1,
        'test_logic':True
    }


    scene = Tunneling3D(**params)
    scene.render()
    print("Rendering over\nSending to tg\n")
    bot = tg()
    bot.video()
