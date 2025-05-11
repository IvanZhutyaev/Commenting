import asyncio
import random
from telethon import TelegramClient, functions
from telethon.errors import ChatAdminRequiredError
import time

api_id, api_hash = input("Введите API: "), input("Введите HASH: ")

client = TelegramClient("programm", api_id, api_hash)

COMMENT_TEXT = """🚀 Ищешь надежную команду для реализации IT-проектов?  
ScriptSquad создает софт, сайты, боты, игры и многое другое — быстро, качественно и под ключ!  
💻 Индивидуальный подход, креативные решения и гарантия результата.  
🔥 Переходи в наш канал (https://t.me/ScriptSquadMain), чтобы заказать разработку или узнать больше:  
#РазработкаНаЗаказ #ScriptSquad #ITРешения  

(Проверь ссылку — там много крутых кейсов! 😉)"""


async def send_comment(peer):
    try:
        # Отправляем комментарий
        await client.send_message(
            peer,
            COMMENT_TEXT,
            link_preview=False
        )
        print(f"Комментарий успешно отправлен пользователю {peer}")
    except Exception as e:
        print(f"Ошибка при отправке комментария пользователю {peer}: {e}")


async def process_stories():
    async for dialog in client.iter_dialogs():
        if dialog.is_group or dialog.is_channel:
            print(f'Обрабатывается диалог: {dialog.title}')
            try:
                async for user in client.iter_participants(dialog.entity):
                    if user.stories_unavailable or user.stories_hidden:
                        continue
                    if user.stories_max_id:
                        try:
                            print(f'Идентификатор пользователя: {user.id}')

                            if hasattr(user, 'stories_max_id') and isinstance(user.stories_max_id, int):
                                max_id_value = user.stories_max_id
                                print(f'Значение max_id для пользователя {user.id}: {max_id_value}')
                            else:
                                print(f'Пользователь {user.id} не имеет параметра stories_max_id или он некорректен.')
                                max_id_value = None

                            if max_id_value and max_id_value > 0:
                                stories = await client(functions.stories.ReadStoriesRequest(
                                    peer=user,
                                    max_id=max_id_value
                                ))
                                print(f"Прочитана история: {user.id}")
                            else:
                                stories = await client(functions.stories.ReadStoriesRequest(
                                    peer=user
                                ))
                                print(f"Прочитана история: {user.id}")

                            print(f'Объект stories: {stories}')

                            # Отправляем комментарий после просмотра сторис
                            await send_comment(user.id)

                            # Генерируем случайную задержку от 3 до 5 минут
                            delay = random.randint(180, 300)
                            print(f"Ожидание {delay} секунд перед следующей сторис...")
                            await asyncio.sleep(delay)

                        except Exception as e:
                            print(f'Ошибка при просмотре историй пользователя {user.id}: {e}')
            except ChatAdminRequiredError:
                print(f'Недостаточно прав для получения участников из: {dialog.title}. Пропуск...')
            except Exception as e:
                print(f'Ошибка при получении участников из: {dialog.title}. {e}')


async def main():
    try:
        async with client:
            await client.start()
            while True:
                await process_stories()
                print()
                await asyncio.sleep(300)  # Пауза 5 минут между циклами обработки диалогов
    except KeyboardInterrupt:
        print("Программа прервана пользователем.")


if __name__ == "__main__":
    asyncio.run(main())