import json
import os
from datetime import datetime
import logging

class StatsLogger:
    def __init__(self):
        self.stats = {
            'total_attempts': 0,
            'successful_views': 0,
            'successful_messages': 0,
            'failed_views': 0,
            'failed_messages': 0,
            'blocked_users': 0,
            'start_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'last_reset': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'daily_stats': {}
        }
        
        # Настройка логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('bot_stats.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Загрузка существующей статистики, если есть
        self.load_stats()
    
    def load_stats(self):
        if os.path.exists('stats.json'):
            try:
                with open('stats.json', 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
            except Exception as e:
                self.logger.error(f"Ошибка при загрузке статистики: {e}")
    
    def save_stats(self):
        try:
            with open('stats.json', 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении статистики: {e}")
    
    def log_story_view(self, user_id, success, error=None):
        self.stats['total_attempts'] += 1
        if success:
            self.stats['successful_views'] += 1
            self.logger.info(f"✅ Успешно просмотрена история пользователя {user_id}")
        else:
            self.stats['failed_views'] += 1
            self.logger.error(f"❌ Ошибка при просмотре истории пользователя {user_id}: {error}")
        self.save_stats()
    
    def log_message_send(self, user_id, success, error=None):
        if success:
            self.stats['successful_messages'] += 1
            self.logger.info(f"✅ Успешно отправлено сообщение пользователю {user_id}")
        else:
            self.stats['failed_messages'] += 1
            self.logger.error(f"❌ Ошибка при отправке сообщения пользователю {user_id}: {error}")
        self.save_stats()
    
    def log_blocked_user(self, user_id):
        self.stats['blocked_users'] += 1
        self.logger.warning(f"⚠️ Пользователь {user_id} заблокировал бота")
        self.save_stats()
    
    def get_daily_stats(self):
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily_stats']:
            self.stats['daily_stats'][today] = {
                'views': 0,
                'messages': 0,
                'errors': 0
            }
        return self.stats['daily_stats'][today]
    
    def print_summary(self):
        total_time = datetime.now() - datetime.strptime(self.stats['start_time'], '%Y-%m-%d %H:%M:%S')
        hours = total_time.total_seconds() / 3600
        
        summary = f"""
📊 Статистика работы бота:
⏱ Время работы: {hours:.2f} часов
👥 Всего попыток: {self.stats['total_attempts']}
✅ Успешных просмотров историй: {self.stats['successful_views']}
✅ Успешных отправок сообщений: {self.stats['successful_messages']}
❌ Неудачных просмотров: {self.stats['failed_views']}
❌ Неудачных отправок: {self.stats['failed_messages']}
🚫 Заблокировавших пользователей: {self.stats['blocked_users']}
        """
        self.logger.info(summary)
        return summary 