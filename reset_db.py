import sqlite3
import os

# Удаляем старую БД если есть
if os.path.exists('diary.db'):
    os.remove('diary.db')
    print('✅ Старая БД удалена')

print('✅ Готово! Теперь запускай python app.py')