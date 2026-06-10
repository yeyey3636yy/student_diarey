from app import app, db, Student, Grade
from datetime import datetime

with app.app_context():
    # Очищаем старые данные (опционально)
    Grade.query.delete()
    Student.query.delete()
    
    # ==================== ДОБАВЛЯЕМ СТУДЕНТОВ ====================
    students = [
        {'full_name': 'Иван Петров', 'group': 'П-41', 'parent_name': 'Елена Петрова', 'parent_phone': '+7-999-111-22-33'},
        {'full_name': 'Анна Сидорова', 'group': 'П-41', 'parent_name': 'Мария Сидорова', 'parent_phone': '+7-999-222-33-44'},
        {'full_name': 'Дмитрий Козлов', 'group': 'П-42', 'parent_name': 'Ольга Козлова', 'parent_phone': '+7-999-333-44-55'},
        {'full_name': 'Елена Морозова', 'group': 'П-42', 'parent_name': 'Сергей Морозов', 'parent_phone': '+7-999-444-55-66'},
        {'full_name': 'Алексей Новиков', 'group': 'П-41', 'parent_name': 'Татьяна Новикова', 'parent_phone': '+7-999-555-66-77'},
        {'full_name': 'София Андреева', 'group': 'П-41', 'parent_name': 'Андрей Андреев', 'parent_phone': '+7-999-666-77-88'},
        {'full_name': 'Максим Воронов', 'group': 'П-42', 'parent_name': 'Ирина Воронова', 'parent_phone': '+7-999-777-88-99'},
        {'full_name': 'Полина Григорьева', 'group': 'П-42', 'parent_name': 'Наталья Григорьева', 'parent_phone': '+7-999-888-99-00'},
    ]
    
    student_objects = []
    for s in students:
        student = Student(
            full_name=s['full_name'],
            group=s['group'],
            date_of_birth='2006-01-01',
            parent_name=s['parent_name'],
            parent_phone=s['parent_phone']
        )
        db.session.add(student)
        student_objects.append(student)
    
    db.session.commit()
    print(f"✅ Добавлено {len(students)} студентов")
    
    # ==================== ДОБАВЛЯЕМ ОЦЕНКИ ====================
    subjects = ['Математика', 'Физика', 'Информатика', 'Русский язык', 'Английский язык', 'История']
    
    # Для каждого студента добавляем оценки
    grades_data = [
        # Иван Петров
        {'student_name': 'Иван Петров', 'grades': [(5, 'Математика'), (4, 'Физика'), (5, 'Информатика'), (4, 'Русский язык'), (5, 'Английский язык')]},
        # Анна Сидорова
        {'student_name': 'Анна Сидорова', 'grades': [(5, 'Математика'), (5, 'Физика'), (4, 'Информатика'), (5, 'Русский язык'), (5, 'Английский язык'), (4, 'История')]},
        # Дмитрий Козлов
        {'student_name': 'Дмитрий Козлов', 'grades': [(4, 'Математика'), (3, 'Физика'), (4, 'Информатика'), (3, 'Русский язык'), (4, 'Английский язык')]},
        # Елена Морозова
        {'student_name': 'Елена Морозова', 'grades': [(5, 'Математика'), (5, 'Физика'), (5, 'Информатика'), (5, 'Русский язык'), (5, 'Английский язык'), (5, 'История')]},
        # Алексей Новиков
        {'student_name': 'Алексей Новиков', 'grades': [(3, 'Математика'), (3, 'Физика'), (4, 'Информатика'), (3, 'Русский язык'), (3, 'Английский язык')]},
        # София Андреева
        {'student_name': 'София Андреева', 'grades': [(5, 'Математика'), (4, 'Физика'), (5, 'Информатика'), (5, 'Русский язык'), (4, 'Английский язык'), (5, 'История')]},
        # Максим Воронов
        {'student_name': 'Максим Воронов', 'grades': [(4, 'Математика'), (4, 'Физика'), (3, 'Информатика'), (4, 'Русский язык'), (4, 'Английский язык')]},
        # Полина Григорьева
        {'student_name': 'Полина Григорьева', 'grades': [(5, 'Математика'), (5, 'Физика'), (5, 'Информатика'), (4, 'Русский язык'), (5, 'Английский язык'), (5, 'История')]},
    ]
    
    total_grades = 0
    for gd in grades_data:
        student = Student.query.filter_by(full_name=gd['student_name']).first()
        if student:
            for grade_val, subject in gd['grades']:
                grade = Grade(
                    student_id=student.id,
                    subject=subject,
                    grade=grade_val,
                    date=datetime.now().strftime('%Y-%m-%d'),
                    comment='Оценка за семестр'
                )
                db.session.add(grade)
                total_grades += 1
    
    db.session.commit()
    print(f"✅ Добавлено {total_grades} оценок")
    
    # ==================== СТАТИСТИКА ====================
    print("\n" + "="*50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*50)
    
    students_count = Student.query.count()
    grades_count = Grade.query.count()
    avg_grade = db.session.query(db.func.avg(Grade.grade)).scalar() or 0
    
    print(f"👨‍🎓 Студентов: {students_count}")
    print(f"📝 Оценок: {grades_count}")
    print(f"📈 Средний балл: {round(avg_grade, 2)}")
    
    print("\n🏆 ТОП СТУДЕНТОВ:")
    top = db.session.query(
        Student.full_name,
        db.func.avg(Grade.grade).label('avg')
    ).join(Grade).group_by(Student.id).order_by(db.desc('avg')).limit(5).all()
    
    for i, student in enumerate(top, 1):
        print(f"  {i}. {student.full_name} — средний балл: {round(student.avg, 2)}")