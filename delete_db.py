import os
import sqlite3

# Удаляем файл БД если есть
db_files = ['diary.db', 'instance/diary.db']

for file in db_files:
    if os.path.exists(file):
        os.remove(file)
        print(f'✅ Удалён: {file}')

print('✅ База данных удалена! Теперь запускай python app.py')