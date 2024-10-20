from telegram import Update
from telegram.ext import Application, CommandHandler
from Tunneling import Tunneling3D
from tg_bot import tg
import asyncio

async def start(update: Update, context) -> None:
    await update.message.reply_text("Привет! Отправь команду /render для начала рендеринга.")

async def render(update, context):
    await update.message.reply_text("Запуск рендеринга...")
    params = {}

    if len(context.args) > 0:
        for arg in context.args:
            try:
                key, value = arg.split('=')
                try:
                    params[key] = float(value)
                except ValueError:
                   params[key] = value
                
            except ValueError:
                await update.message.reply_text(f"Ошибка в параметре: {arg}")
                return

    scene = Tunneling3D(**params)
    scene.render()
    await update.message.reply_text("Рендеринг завершен.")
    bot = tg()
    bot.video()

    
def main():
    bot = tg()
    token , _ = bot.get_token()
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("render", render))

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
