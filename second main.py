import asyncio
import random
import time
from datetime import datetime
from telethon import TelegramClient, functions, errors
from telethon.tl.types import InputPeerUser


class AntiSpamProtection:
    def __init__(self):
        self.last_action_time = 0
        self.daily_limit = 150  # Лимит действий в день
        self.actions_count = 0
        self.blacklist = set()  # Для хранения проблемных пользователей

    async def safe_delay(self):
        """Случайная задержка с прогрессивным увеличением при приближении к лимиту"""
        base_delay = random.uniform(5, 8)  # Базовая задержка 5-8 секунд

        # Увеличиваем задержку по мере приближения к дневному лимиту
        progress = self.actions_count / self.daily_limit
        if progress > 0.7:
            base_delay *= (1 + progress)  # Увеличиваем задержку на 30-100%

        # Добавляем небольшую случайную вариацию
        delay = base_delay * random.uniform(0.9, 1.1)

        print(f"Задержка: {delay:.2f} сек. (Прогресс: {progress:.1%})")
        await asyncio.sleep(delay)

    def check_daily_limit(self):
        """Проверка не превышен ли дневной лимит"""
        if self.actions_count >= self.daily_limit:
            raise Exception("Достигнут дневной лимит действий")


class StoryViewer:
    def __init__(self, client, anti_spam):
        self.client = client
        self.anti_spam = anti_spam
        self.start_time = time.time()

        # Конфигурация
        self.comment_text = """🚀 Ищешь надежную команду для реализации IT-проектов?  
ScriptSquad создает софт, сайты, боты, игры и многое другое — быстро, качественно и под ключ!  
💻 Индивидуальный подход, креативные решения и гарантия результата.  
🔥 Переходи в наш [канал](https://t.me/ScriptSquadMain), чтобы заказать разработку или узнать больше:  
#РазработкаНаЗаказ #ScriptSquad #ITРешения  

(Проверь ссылку — там много крутых кейсов! 😉)"""

        # Статистика
        self.success_count = 0
        self.error_count = 0

    async def send_comment(self, user_id):
        """Безопасная отправка комментария"""
        try:
            if user_id in self.anti_spam.blacklist:
                print(f"Пользователь {user_id} в черном списке, пропуск")
                return False

            await self.client.send_message(
                entity=user_id,
                message=self.comment_text,
                link_preview=False,
                schedule=random.randint(300, 1800)  # Отложенная отправка
            )
            print(f"✉️ Комментарий запланирован для {user_id}")
            return True
        except errors.FloodWaitError as e:
            print(f"⚠️ FloodWait на {e.seconds} сек. для {user_id}")
            await asyncio.sleep(e.seconds + random.uniform(10, 30))
            return False
        except errors.UserPrivacyRestrictedError:
            print(f"🔒 Пользователь {user_id} ограничил приватность")
            self.anti_spam.blacklist.add(user_id)
            return False
        except Exception as e:
            print(f"❌ Ошибка при отправке {user_id}: {str(e)}")
            self.error_count += 1
            return False

    async def view_stories(self, user):
        """Просмотр сторис с обработкой ошибок"""
        try:
            self.anti_spam.check_daily_limit()

            if user.stories_unavailable or user.stories_hidden:
                return False

            max_id = getattr(user, 'stories_max_id', None)
            if max_id and isinstance(max_id, int) and max_id > 0:
                await self.client(functions.stories.ReadStoriesRequest(
                    peer=user,
                    max_id=max_id
                ))
            else:
                await self.client(functions.stories.ReadStoriesRequest(
                    peer=user
                ))

            print(f"👀 Просмотрены сторис пользователя {user.id}")
            self.success_count += 1
            self.anti_spam.actions_count += 1
            return True
        except errors.FloodWaitError as e:
            print(f"⏳ Ожидание {e.seconds} сек. из-за FloodWait")
            await asyncio.sleep(e.seconds + random.uniform(5, 15))
            return False
        except Exception as e:
            print(f"⚠️ Ошибка просмотра сторис {user.id}: {str(e)}")
            return False

    async def process_user(self, user):
        """Обработка одного пользователя"""
        if random.random() < 0.05:  # 5% случайных пропусков
            print(f"🎲 Случайный пропуск пользователя {user.id}")
            return

        if await self.view_stories(user):
            if random.random() < 0.7:  # 70% шанс отправить комментарий
                await self.send_comment(user.id)
            await self.anti_spam.safe_delay()

    async def process_dialog(self, dialog):
        """Обработка одного диалога/чата"""
        if not dialog.is_group and not dialog.is_channel:
            return

        print(f"\n📌 Обработка: {dialog.title}")
        try:
            participants = await self.client.get_participants(dialog, limit=50)
            random.shuffle(participants)  # Случайный порядок

            for user in participants:
                if time.time() - self.start_time > 86400:  # 24 часа
                    print("🕒 Истекло время работы (24 часа)")
                    return False

                await self.process_user(user)

                # Периодическая пауза
                if self.success_count % 10 == 0:
                    nap = random.randint(60, 180)
                    print(f"😴 Долгая пауза {nap} сек...")
                    await asyncio.sleep(nap)

            return True
        except errors.ChatAdminRequiredError:
            print(f"⛔ Нет прав админа в {dialog.title}")
        except Exception as e:
            print(f"⚠️ Ошибка обработки {dialog.title}: {str(e)}")
        return False

    async def run(self):
        """Основной цикл работы"""
        try:
            dialogs = await self.client.get_dialogs(limit=30)
            random.shuffle(dialogs)

            for dialog in dialogs:
                if not await self.process_dialog(dialog):
                    break

                # Большая пауза между чатами
                await asyncio.sleep(random.randint(300, 600))

        except Exception as e:
            print(f"🔥 Критическая ошибка: {str(e)}")
        finally:
            print(f"\n📊 Итоги: Успешно {self.success_count}, Ошибок {self.error_count}")


async def main():
    print("""
    ███████╗████████╗ ██████╗ ██████╗ ██╗   ██╗
    ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗╚██╗ ██╔╝
    ███████╗   ██║   ██║   ██║██████╔╝ ╚████╔╝ 
    ╚════██║   ██║   ██║   ██║██╔══██╗  ╚██╔╝  
    ███████║   ██║   ╚██████╔╝██║  ██║   ██║   
    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   
    """)

    api_id = input("Введите API ID: ").strip()
    api_hash = input("Введите API HASH: ").strip()

    async with TelegramClient("story_viewer", api_id, api_hash) as client:
        anti_spam = AntiSpamProtection()
        viewer = StoryViewer(client, anti_spam)
        await viewer.run()


if __name__ == "__main__":
    asyncio.run(main())