from app import app, db, Student, Grade
from datetime import datetime
import random

with app.app_context():
    # ==================== ДОБАВЛЯЕМ ЕЩЁ СТУДЕНТОВ ====================
    new_students = [
        {'full_name': 'Артём Белов', 'group': 'П-41', 'parent_name': 'Наталья Белова', 'parent_phone': '+7-999-123-45-67'},
        {'full_name': 'Виктория Кузнецова', 'group': 'П-41', 'parent_name': 'Елена Кузнецова', 'parent_phone': '+7-999-234-56-78'},
        {'full_name': 'Даниил Соколов', 'group': 'П-42', 'parent_name': 'Ирина Соколова', 'parent_phone': '+7-999-345-67-89'},
        {'full_name': 'Екатерина Михайлова', 'group': 'П-42', 'parent_name': 'Ольга Михайлова', 'parent_phone': '+7-999-456-78-90'},
        {'full_name': 'Никита Фёдоров', 'group': 'П-41', 'parent_name': 'Анна Фёдорова', 'parent_phone': '+7-999-567-89-01'},
        {'full_name': 'Анастасия Егорова', 'group': 'П-41', 'parent_name': 'Татьяна Егорова', 'parent_phone': '+7-999-678-90-12'},
        {'full_name': 'Владимир Павлов', 'group': 'П-42', 'parent_name': 'Светлана Павлова', 'parent_phone': '+7-999-789-01-23'},
        {'full_name': 'Мария Семёнова', 'group': 'П-41', 'parent_name': 'Людмила Семёнова', 'parent_phone': '+7-999-890-12-34'},
        {'full_name': 'Кирилл Тимофеев', 'group': 'П-42', 'parent_name': 'Евгения Тимофеева', 'parent_phone': '+7-999-901-23-45'},
        {'full_name': 'Полина Фролова', 'group': 'П-41', 'parent_name': 'Маргарита Фролова', 'parent_phone': '+7-999-012-34-56'},
        {'full_name': 'Андрей Сергеев', 'group': 'П-42', 'parent_name': 'Валентина Сергеева', 'parent_phone': '+7-999-111-22-33'},
        {'full_name': 'Дарья Гусева', 'group': 'П-41', 'parent_name': 'Инна Гусева', 'parent_phone': '+7-999-222-33-44'},
        {'full_name': 'Матвей Емельянов', 'group': 'П-42', 'parent_name': 'Оксана Емельянова', 'parent_phone': '+7-999-333-44-55'},
        {'full_name': 'Алиса Романова', 'group': 'П-41', 'parent_name': 'Вера Романова', 'parent_phone': '+7-999-444-55-66'},
        {'full_name': 'Сергей Алексеев', 'group': 'П-42', 'parent_name': 'Лариса Алексеева', 'parent_phone': '+7-999-555-66-77'},
    ]
    
    added_students = []
    for s in new_students:
        # Проверяем, нет ли уже такого студента
        existing = Student.query.filter_by(full_name=s['full_name']).first()
        if not existing:
            student = Student(
                full_name=s['full_name'],
                group=s['group'],
                date_of_birth=f"{random.randint(2005, 2007)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                parent_name=s['parent_name'],
                parent_phone=s['parent_phone']
            )
            db.session.add(student)
            added_students.append(student)
    
    db.session.commit()
    print(f"✅ Добавлено {len(added_students)} новых студентов!")
    
    # ==================== ДОБАВЛЯЕМ ИМ ОЦЕНКИ ====================
    subjects = ['Математика', 'Физика', 'Информатика', 'Русский язык', 'Английский язык', 'История']
    grades_values = [5, 5, 4, 4, 3]
    
    total_new_grades = 0
    for student in added_students:
        # Каждому новому студенту добавляем 5-8 оценок
        num_grades = random.randint(5, 8)
        for _ in range(num_grades):
            grade = Grade(
                student_id=student.id,
                subject=random.choice(subjects),
                grade=random.choice(grades_values),
                date=datetime.now().strftime('%Y-%m-%d'),
                comment='Оценка за семестр'
            )
            db.session.add(grade)
            total_new_grades += 1
    
    db.session.commit()
    print(f"✅ Добавлено {total_new_grades} новых оценок!")
    
    # ==================== ИТОГОВАЯ СТАТИСТИКА ====================
    print("\n" + "="*55)
    print("📊 ОБНОВЛЁННАЯ СТАТИСТИКА")
    print("="*55)
    
    total_students = Student.query.count()
    total_grades = Grade.query.count()
    avg_grade = db.session.query(db.func.avg(Grade.grade)).scalar() or 0
    
    print(f"👨‍🎓 Всего студентов: {total_students}")
    print(f"📝 Всего оценок: {total_grades}")
    print(f"📈 Средний балл: {round(avg_grade, 2)}")
    
    # Группы
    print("\n📚 ПО ГРУППАМ:")
    groups = db.session.query(Student.group, db.func.count(Student.id)).group_by(Student.group).all()
    for group, count in groups:
        avg = db.session.query(db.func.avg(Grade.grade)).join(Student).filter(Student.group == group).scalar() or 0
        print(f"  {group}: {count} студентов, средний балл: {round(avg, 2)}")
    
    # Топ 5 студентов
    print("\n🏆 ТОП-5 СТУДЕНТОВ:")
    top = db.session.query(
        Student.full_name,
        Student.group,
        db.func.avg(Grade.grade).label('avg')
    ).join(Grade).group_by(Student.id).order_by(db.desc('avg')).limit(5).all()
    
    for i, student in enumerate(top, 1):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
        print(f"  {medal} {i}. {student.full_name} ({student.group}) — {round(student.avg, 2)}")