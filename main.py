import asyncio
import random
import os
from telethon import TelegramClient, functions
from telethon.errors import (
    ChatAdminRequiredError, 
    UserBlockedError, 
    FloodWaitError,
    SessionPasswordNeededError,
    PhoneCodeInvalidError
)
from dotenv import load_dotenv
import time
from stats_logger import StatsLogger

# Загрузка переменных окружения
load_dotenv()

# Получение API данных из переменных окружения
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')

# Проверка наличия API данных
if not api_id or not api_hash:
    print("Ошибка: API_ID и API_HASH должны быть установлены в файле .env")
    exit(1)

# Получение текста комментария
COMMENT_TEXT = os.getenv('COMMENT_TEXT')
if not COMMENT_TEXT:
    print("Ошибка: COMMENT_TEXT должен быть установлен в файле .env")
    exit(1)

# Конфигурация
MAX_CONCURRENT_REQUESTS = int(os.getenv('MAX_CONCURRENT_REQUESTS', 5))
DAILY_LIMIT = int(os.getenv('DAILY_LIMIT', 150))
MIN_DELAY = int(os.getenv('MIN_DELAY', 180))
MAX_DELAY = int(os.getenv('MAX_DELAY', 300))
MAX_MESSAGES = 100  # Максимальное количество сообщений

client = TelegramClient("programm", api_id, api_hash)
stats_logger = StatsLogger()

async def send_comment(peer):
    try:
        # Проверяем, не превышен ли лимит сообщений
        if stats_logger.stats['successful_messages'] >= MAX_MESSAGES:
            print(f"Достигнут лимит в {MAX_MESSAGES} сообщений. Прекращаем отправку.")
            return False

        # Отправляем комментарий
        await client.send_message(
            peer,
            COMMENT_TEXT,
            link_preview=False
        )
        stats_logger.log_message_send(peer, True)
        print(f"Комментарий успешно отправлен пользователю {peer}")
        print(f"Отправлено сообщений: {stats_logger.stats['successful_messages']} из {MAX_MESSAGES}")
        return True
    except UserBlockedError:
        stats_logger.log_blocked_user(peer)
        print(f"Пользователь {peer} заблокировал бота")
        return False
    except FloodWaitError as e:
        wait_time = e.seconds
        print(f"Достигнут лимит запросов. Ожидание {wait_time} секунд...")
        await asyncio.sleep(wait_time)
        stats_logger.log_message_send(peer, False, f"FloodWait: {wait_time} секунд")
        return False
    except Exception as e:
        stats_logger.log_message_send(peer, False, str(e))
        print(f"Ошибка при отправке комментария пользователю {peer}: {e}")
        return False


async def process_stories():
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async for dialog in client.iter_dialogs():
        # Проверяем, не достигнут ли лимит сообщений
        if stats_logger.stats['successful_messages'] >= MAX_MESSAGES:
            print(f"Достигнут лимит в {MAX_MESSAGES} сообщений. Завершаем работу.")
            return

        if dialog.is_group or dialog.is_channel:
            print(f'Обрабатывается диалог: {dialog.title}')
            try:
                async for user in client.iter_participants(dialog.entity):
                    # Проверяем лимит перед каждой итерацией
                    if stats_logger.stats['successful_messages'] >= MAX_MESSAGES:
                        print(f"Достигнут лимит в {MAX_MESSAGES} сообщений. Завершаем обработку.")
                        return

                    if user.stories_unavailable or user.stories_hidden:
                        continue
                    if user.stories_max_id:
                        async with semaphore:  # Ограничение одновременных запросов
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
                                    stats_logger.log_story_view(user.id, True)
                                    print(f"Прочитана история: {user.id}")
                                else:
                                    stories = await client(functions.stories.ReadStoriesRequest(
                                        peer=user
                                    ))
                                    stats_logger.log_story_view(user.id, True)
                                    print(f"Прочитана история: {user.id}")

                                print(f'Объект stories: {stories}')

                                # Отправляем комментарий после просмотра сторис
                                message_sent = await send_comment(user.id)
                                if not message_sent:
                                    continue

                                # Генерируем случайную задержку
                                delay = random.randint(MIN_DELAY, MAX_DELAY)
                                print(f"Ожидание {delay} секунд перед следующей сторис...")
                                await asyncio.sleep(delay)

                            except FloodWaitError as e:
                                wait_time = e.seconds
                                print(f"Достигнут лимит запросов. Ожидание {wait_time} секунд...")
                                await asyncio.sleep(wait_time)
                                stats_logger.log_story_view(user.id, False, f"FloodWait: {wait_time} секунд")
                            except Exception as e:
                                stats_logger.log_story_view(user.id, False, str(e))
                                print(f'Ошибка при просмотре историй пользователя {user.id}: {e}')
            except ChatAdminRequiredError:
                print(f'Недостаточно прав для получения участников из: {dialog.title}. Пропуск...')
            except Exception as e:
                print(f'Ошибка при получении участников из: {dialog.title}. {e}')


async def main():
    try:
        async with client:
            try:
                await client.start()
                print("Бот запущен. Начинаем работу...")
                print(f"Лимит сообщений установлен: {MAX_MESSAGES}")
                print(stats_logger.print_summary())
                
                while stats_logger.stats['successful_messages'] < MAX_MESSAGES:
                    await process_stories()
                    print("\nЗавершен цикл обработки. Статистика:")
                    print(stats_logger.print_summary())
                    
                    if stats_logger.stats['successful_messages'] >= MAX_MESSAGES:
                        print(f"\nДостигнут лимит в {MAX_MESSAGES} сообщений. Завершаем работу.")
                        break
                        
                    print("\nОжидание 5 минут перед следующим циклом...")
                    await asyncio.sleep(300)  # Пауза 5 минут между циклами обработки диалогов
            except SessionPasswordNeededError:
                print("Требуется двухфакторная аутентификация. Пожалуйста, введите пароль:")
                password = input()
                await client.sign_in(password=password)
            except PhoneCodeInvalidError:
                print("Неверный код подтверждения. Пожалуйста, перезапустите бота.")
                return
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем.")
        print("Итоговая статистика:")
        print(stats_logger.print_summary())
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")
        print("Итоговая статистика:")
        print(stats_logger.print_summary())


if __name__ == "__main__":
    asyncio.run(main())