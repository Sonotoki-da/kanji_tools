# Получить api_id и api_hash вот здесь https://core.telegram.org/api/obtaining_api_id#obtaining-api-id
# python 3.9.5+
# Необходимые модули: pip install telethon tzdata


# import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from telethon import TelegramClient, events

# logging.basicConfig(
#     format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
#     level=logging.DEBUG
# )

# вводить свой api_id, api_hash
api_id = 1234567
api_hash = '123456789abcd'

client = TelegramClient('my_chat_logger', api_id, api_hash).start()


@client.on(events.NewMessage(outgoing=True))
async def all_outgoing_message_handler(event: events.NewMessage.Event):
    with open(
        datetime.now(ZoneInfo('Asia/Tashkent'))
        .strftime('%Y-%m-%d my telegram log.txt'),
        mode='a+',
        encoding='utf-8'
    ) as f:
        try:
            user = await event.get_chat()
            who = 'пользователь ' + user.first_name
        except:
            who = 'группа ' + event.message.chat.title

        f.write(
            f"Кому: {who}, "
            f"когда: {event.message.date.strftime('%Y-%m-%d %H:%M:%S')}: "
            f"{event.message.text}\n"
        )

try:
    print("Ctrl+c чтобы остановить")
    client.run_until_disconnected()
finally:
    client.disconnect()
