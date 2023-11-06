from telegram import Bot

API_TOKEN = '1968085479:AAEck4QaWFrY9Bl7tNKRaqF3lNe0dIrr3Kg'
bot = Bot(token=API_TOKEN)

async def send_telegram_message(message_text="test"):
    chat_id = '1956916092'
    # 메시지를 보내고 응답을 기다리기 위해 await 키워드를 사용합니다.
    await bot.send_message(chat_id=chat_id, text=message_text)

# 비동기 함수를 실행합니다.
import asyncio

asyncio.run(send_telegram_message())
