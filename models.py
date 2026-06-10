from database import db, User, Student, Grade, Subject, Schedule
from datetime import datetime

class GradeCalculator:
    """Класс для расчёта успеваемости"""
    
    @staticmethod
    def calculate_average(grades_list):
        """Расчёт среднего арифметического"""
        if not grades_list:
            return 0
        return sum(grades_list) / len(grades_list)
    
    @staticmethod
    def get_grade_distribution(grades):
        """Получить распределение оценок"""
        distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for grade in grades:
            distribution[grade] += 1
        return distribution
    
    @staticmethod
    def get_performance_level(average):
        """Определить уровень успеваемости"""
        if average >= 4.5:
            return {'level': 'Отлично', 'color': '#28a745', 'icon': 'fa-trophy'}
        elif average >= 3.5:
            return {'level': 'Хорошо', 'color': '#17a2b8', 'icon': 'fa-star'}
        elif average >= 2.5:
            return {'level': 'Удовлетворительно', 'color': '#ffc107', 'icon': 'fa-exclamation-triangle'}
        else:
            return {'level': 'Нужно подтянуть', 'color': '#dc3545', 'icon': 'fa-times-circle'}


class DataExporter:
    """Класс для экспорта данных"""
    
    @staticmethod
    def export_students_to_csv(students):
        """Экспорт студентов в CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'ФИО', 'Группа', 'Дата рождения', 'Родитель', 'Телефон'])
        
        for student in students:
            writer.writerow([
                student.id, student.full_name, student.group,
                student.date_of_birth or '-', student.parent_name or '-',
                student.parent_phone or '-'
            ])
        
        return output.getvalue()
    
    @staticmethod
    def export_grades_to_csv(grades):
        """Экспорт оценок в CSV"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID студента', 'Студент', 'Предмет', 'Оценка', 'Дата', 'Комментарий'])
        
        for grade in grades:
            writer.writerow([
                grade.student_id, grade.student.full_name, grade.subject,
                grade.grade, grade.date, grade.comment or '-'
            ])
        
        return output.getvalue()


class Validators:
    """Класс для валидации данных"""
    
    @staticmethod
    def validate_grade(grade):
        """Проверка корректности оценки"""
        try:
            grade_num = int(grade)
            return 1 <= grade_num <= 5
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_group(group):
        """Проверка формата группы"""
        import re
        pattern = r'^[A-Za-zА-Яа-я0-9\-]{2,10}$'
        return bool(re.match(pattern, group)) if group else False
    
    @staticmethod
    def validate_phone(phone):
        """Проверка номера телефона"""
        import re
        pattern = r'^\+?[0-9\s\-\(\)]{10,15}$'
        return bool(re.match(pattern, phone)) if phone else True


def get_statistics():
    """Получение общей статистики"""
    students_count = Student.query.count()
    grades_count = Grade.query.count()
    
    # Средний балл
    avg_grade = db.session.query(db.func.avg(Grade.grade)).scalar() or 0
    
    # Количество отличников (средний балл > 4.5)
    excellent_students = 0
    for student in Student.query.all():
        if student.get_average_grade() >= 4.5:
            excellent_students += 1
    
    return {
        'students_count': students_count,
        'grades_count': grades_count,
        'avg_grade': round(avg_grade, 2),
        'excellent_students': excellent_students
    }