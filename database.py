from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ==================== МОДЕЛИ БАЗЫ ДАННЫХ ====================

class User(UserMixin, db.Model):
    """Модель пользователя (админ, учитель, ученик, родитель)"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')  # admin, teacher, student, parent
    full_name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(20))
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Student(db.Model):
    """Модель студента"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.String(20))
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    created_at = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d'))
    
    # Связь с оценками
    grades = db.relationship('Grade', backref='student', lazy=True)
    
    def get_average_grade(self):
        """Получить средний балл студента"""
        if not self.grades:
            return 0
        total = sum(grade.grade for grade in self.grades)
        return round(total / len(self.grades), 2)
    
    def __repr__(self):
        return f'<Student {self.full_name}>'


class Grade(db.Model):
    """Модель оценки"""
    __tablename__ = 'grades'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.String(200))
    
    def __repr__(self):
        return f'<Grade {self.grade} for Student {self.student_id}>'


class Subject(db.Model):
    """Модель предмета"""
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    teacher = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Subject {self.name}>'


class Schedule(db.Model):
    """Модель расписания"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (пн-вс)
    lesson_number = db.Column(db.Integer, nullable=False)  # 1-8
    subject = db.Column(db.String(50), nullable=False)
    classroom = db.Column(db.String(20))
    teacher = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Schedule {self.group} - {self.day_of_week}>'


def init_db(app):
    """Инициализация базы данных"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Создание тестовых предметов
        subjects = ['Математика', 'Физика', 'Информатика', 'Русский язык', 'Английский язык', 'История']
        for subj in subjects:
            if not Subject.query.filter_by(name=subj).first():
                db.session.add(Subject(name=subj, teacher='Преподаватель'))
        
        # Создание тестового расписания
        if Schedule.query.count() == 0:
            schedule_data = [
                # Понедельник (0)
                {'group': 'П-41', 'day': 0, 'lesson': 1, 'subject': 'Математика', 'classroom': '301'},
                {'group': 'П-41', 'day': 0, 'lesson': 2, 'subject': 'Физика', 'classroom': '205'},
                {'group': 'П-41', 'day': 0, 'lesson': 3, 'subject': 'Информатика', 'classroom': '404'},
                # Вторник (1)
                {'group': 'П-41', 'day': 1, 'lesson': 1, 'subject': 'Русский язык', 'classroom': '101'},
                {'group': 'П-41', 'day': 1, 'lesson': 2, 'subject': 'Английский язык', 'classroom': '201'},
                {'group': 'П-41', 'day': 1, 'lesson': 3, 'subject': 'История', 'classroom': '105'},
            ]
            
            for item in schedule_data:
                db.session.add(Schedule(
                    group=item['group'],
                    day_of_week=item['day'],
                    lesson_number=item['lesson'],
                    subject=item['subject'],
                    classroom=item['classroom']
                ))
        
        db.session.commit()
        print("✅ База данных инициализирована")