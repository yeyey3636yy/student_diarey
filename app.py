from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ==================== МОДЕЛИ ====================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='student')
    full_name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(20))
    subject = db.Column(db.String(50))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    group = db.Column(db.String(20), nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group = db.Column(db.String(20), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    lesson_number = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    classroom = db.Column(db.String(20))

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    quarter = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)
    teacher_name = db.Column(db.String(100))
    
    student = db.relationship('Student', backref='grades')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.String(20), default=datetime.now().strftime('%Y-%m-%d %H:%M'))
    
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ФУНКЦИЯ ФОРМАТИРОВАНИЯ ====================

def format_grade(g):
    if g == -1:
        return 'Н'
    elif g == -2:
        return 'П'
    elif g == -3:
        return 'Б'
    else:
        return str(g)

# ==================== СОЗДАНИЕ БД ====================

with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', full_name='Администратор', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("✅ Админ создан: admin / admin123")
    
    teachers = [
        {'username': 'teacher_phys', 'full_name': 'Иван Сергеевич', 'subject': 'Физика', 'password': 'phys123'},
        {'username': 'teacher_math', 'full_name': 'Мария Ивановна', 'subject': 'Алгебра', 'password': 'math123'},
        {'username': 'teacher_rus', 'full_name': 'Елена Владимировна', 'subject': 'Русский язык', 'password': 'rus123'},
        {'username': 'teacher_eng', 'full_name': 'Ольга Дмитриевна', 'subject': 'Английский язык', 'password': 'eng123'},
        {'username': 'teacher_history', 'full_name': 'Дмитрий Николаевич', 'subject': 'История', 'password': 'history123'},
        {'username': 'teacher_inf', 'full_name': 'Алексей Петрович', 'subject': 'Информатика', 'password': 'inf123'},
    ]
    for t in teachers:
        if not User.query.filter_by(username=t['username']).first():
            teacher = User(username=t['username'], full_name=t['full_name'], role='teacher', subject=t['subject'])
            teacher.set_password(t['password'])
            db.session.add(teacher)
            print(f"✅ Учитель: {t['username']} / {t['password']}")
    
    students_data = [
        {'username': 'ivanov', 'full_name': 'Иван Иванов', 'group': 'И-23-2к', 'password': 'ivan123'},
        {'username': 'petrov', 'full_name': 'Петр Петров', 'group': 'И-23-2к', 'password': 'petr123'},
        {'username': 'sidorov', 'full_name': 'Сидор Сидоров', 'group': 'Э-22-2', 'password': 'sidor123'},
        {'username': 'kozlov', 'full_name': 'Алексей Козлов', 'group': 'Э-22-2', 'password': 'kozlov123'},
    ]
    for s in students_data:
        if not User.query.filter_by(username=s['username']).first():
            student = User(username=s['username'], full_name=s['full_name'], role='student', group=s['group'])
            student.set_password(s['password'])
            db.session.add(student)
            print(f"✅ Ученик: {s['username']} / {s['password']}")
        
        if not Student.query.filter_by(full_name=s['full_name']).first():
            db.session.add(Student(full_name=s['full_name'], group=s['group']))
    
    if Schedule.query.count() == 0:
        schedule_data = [
            {'group': 'И-23-2к', 'day_of_week': 0, 'lesson_number': 1, 'subject': 'Алгебра', 'teacher': 'Мария Ивановна', 'classroom': '201'},
            {'group': 'И-23-2к', 'day_of_week': 0, 'lesson_number': 2, 'subject': 'Физика', 'teacher': 'Иван Сергеевич', 'classroom': '205'},
            {'group': 'И-23-2к', 'day_of_week': 0, 'lesson_number': 3, 'subject': 'Информатика', 'teacher': 'Алексей Петрович', 'classroom': '404'},
            {'group': 'И-23-2к', 'day_of_week': 0, 'lesson_number': 4, 'subject': 'Алгебра', 'teacher': 'Мария Ивановна', 'classroom': '201'},
            {'group': 'И-23-2к', 'day_of_week': 1, 'lesson_number': 1, 'subject': 'Русский язык', 'teacher': 'Елена Владимировна', 'classroom': '101'},
            {'group': 'И-23-2к', 'day_of_week': 1, 'lesson_number': 2, 'subject': 'Английский язык', 'teacher': 'Ольга Дмитриевна', 'classroom': '305'},
            {'group': 'И-23-2к', 'day_of_week': 1, 'lesson_number': 3, 'subject': 'История', 'teacher': 'Дмитрий Николаевич', 'classroom': '108'},
            {'group': 'И-23-2к', 'day_of_week': 1, 'lesson_number': 4, 'subject': 'Физика', 'teacher': 'Иван Сергеевич', 'classroom': '205'},
            {'group': 'И-23-2к', 'day_of_week': 2, 'lesson_number': 1, 'subject': 'Алгебра', 'teacher': 'Мария Ивановна', 'classroom': '201'},
            {'group': 'И-23-2к', 'day_of_week': 2, 'lesson_number': 2, 'subject': 'Русский язык', 'teacher': 'Елена Владимировна', 'classroom': '101'},
            {'group': 'И-23-2к', 'day_of_week': 2, 'lesson_number': 3, 'subject': 'Физика', 'teacher': 'Иван Сергеевич', 'classroom': '205'},
            {'group': 'И-23-2к', 'day_of_week': 2, 'lesson_number': 4, 'subject': 'Физкультура', 'teacher': 'Сергей Владимирович', 'classroom': 'спортзал'},
            {'group': 'И-23-2к', 'day_of_week': 3, 'lesson_number': 1, 'subject': 'Английский язык', 'teacher': 'Ольга Дмитриевна', 'classroom': '305'},
            {'group': 'И-23-2к', 'day_of_week': 3, 'lesson_number': 2, 'subject': 'История', 'teacher': 'Дмитрий Николаевич', 'classroom': '108'},
            {'group': 'И-23-2к', 'day_of_week': 3, 'lesson_number': 3, 'subject': 'Информатика', 'teacher': 'Алексей Петрович', 'classroom': '404'},
            {'group': 'И-23-2к', 'day_of_week': 3, 'lesson_number': 4, 'subject': 'Алгебра', 'teacher': 'Мария Ивановна', 'classroom': '201'},
            {'group': 'И-23-2к', 'day_of_week': 4, 'lesson_number': 1, 'subject': 'Физика', 'teacher': 'Иван Сергеевич', 'classroom': '205'},
            {'group': 'И-23-2к', 'day_of_week': 4, 'lesson_number': 2, 'subject': 'Русский язык', 'teacher': 'Елена Владимировна', 'classroom': '101'},
            {'group': 'И-23-2к', 'day_of_week': 4, 'lesson_number': 3, 'subject': 'Английский язык', 'teacher': 'Ольга Дмитриевна', 'classroom': '305'},
            {'group': 'И-23-2к', 'day_of_week': 4, 'lesson_number': 4, 'subject': 'История', 'teacher': 'Дмитрий Николаевич', 'classroom': '108'},
            {'group': 'Э-22-2', 'day_of_week': 0, 'lesson_number': 1, 'subject': 'Физика', 'teacher': 'Иван Сергеевич', 'classroom': '205'},
            {'group': 'Э-22-2', 'day_of_week': 0, 'lesson_number': 2, 'subject': 'Алгебра', 'teacher': 'Мария Ивановна', 'classroom': '201'},
            {'group': 'Э-22-2', 'day_of_week': 1, 'lesson_number': 1, 'subject': 'Информатика', 'teacher': 'Алексей Петрович', 'classroom': '404'},
            {'group': 'Э-22-2', 'day_of_week': 1, 'lesson_number': 2, 'subject': 'Физика', 'teacher': 'Иван Сергеевич', 'classroom': '205'},
            {'group': 'Э-22-2', 'day_of_week': 2, 'lesson_number': 1, 'subject': 'Алгебра', 'teacher': 'Мария Ивановна', 'classroom': '201'},
            {'group': 'Э-22-2', 'day_of_week': 3, 'lesson_number': 1, 'subject': 'Русский язык', 'teacher': 'Елена Владимировна', 'classroom': '101'},
            {'group': 'Э-22-2', 'day_of_week': 4, 'lesson_number': 1, 'subject': 'Английский язык', 'teacher': 'Ольга Дмитриевна', 'classroom': '305'},
        ]
        for s in schedule_data:
            db.session.add(Schedule(**s))
        print("✅ Расписание создано")
    
    subjects = ['Алгебра', 'Физика', 'Русский язык', 'Английский язык', 'Информатика', 'История']
    grades_values = [5, 5, 5, 4, 4, 4, 4, 3, 3]
    
    for student in Student.query.all():
        if Grade.query.filter_by(student_id=student.id).count() == 0:
            num_grades = random.randint(6, 12)
            for i in range(num_grades):
                subject = random.choice(subjects)
                grade_val = random.choice(grades_values)
                quarter = 1 if i < num_grades // 2 else 2
                date = f"2026-0{random.randint(1, 5)}-{random.randint(1, 28):02d}"
                db.session.add(Grade(
                    student_id=student.id,
                    subject=subject,
                    grade=grade_val,
                    quarter=quarter,
                    date=date,
                    teacher_name='Учитель'
                ))
    
    db.session.commit()
    
    print("\n✅ БАЗА ДАННЫХ ГОТОВА!")
    print(f"👨‍🎓 Студентов И-23-2к: {Student.query.filter_by(group='И-23-2к').count()}")
    print(f"👨‍🎓 Студентов Э-22-2: {Student.query.filter_by(group='Э-22-2').count()}")

# ==================== МАРШРУТЫ ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Добро пожаловать, {user.full_name}!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher_journal'))
            return redirect(url_for('schedule_view'))
        flash('Неверный логин или пароль', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ==================== АДМИН ====================

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Доступ только для администратора', 'danger')
        return redirect(url_for('index'))
    
    students = Student.query.all()
    teachers = User.query.filter_by(role='teacher').all()
    groups = ['И-23-2к', 'Э-22-2']
    
    students_list = []
    for student in students:
        user = User.query.filter_by(full_name=student.full_name, role='student').first()
        students_list.append({
            'full_name': student.full_name,
            'group': student.group,
            'username': user.username if user else '-',
            'user_id': student.id
        })
    
    return render_template('admin_dashboard.html', 
                         students=students_list,
                         teachers=teachers,
                         groups=groups,
                         current_user=current_user)

@app.route('/admin/add_student', methods=['POST'])
@login_required
def admin_add_student():
    if current_user.role != 'admin':
        flash('Доступ только для администратора', 'danger')
        return redirect(url_for('index'))
    
    full_name = request.form.get('full_name')
    group = request.form.get('group')
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not full_name or not group or not username or not password:
        flash('Заполните все поля', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if User.query.filter_by(username=username).first():
        flash('Пользователь с таким логином уже существует', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    new_user = User(username=username, full_name=full_name, role='student', group=group)
    new_user.set_password(password)
    db.session.add(new_user)
    
    new_student = Student(full_name=full_name, group=group)
    db.session.add(new_student)
    
    db.session.commit()
    flash(f'Студент {full_name} добавлен! Логин: {username}, Пароль: {password}', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_teacher', methods=['POST'])
@login_required
def admin_add_teacher():
    if current_user.role != 'admin':
        flash('Доступ только для администратора', 'danger')
        return redirect(url_for('index'))
    
    full_name = request.form.get('full_name')
    subject = request.form.get('subject')
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not full_name or not subject or not username or not password:
        flash('Заполните все поля', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if User.query.filter_by(username=username).first():
        flash('Пользователь с таким логином уже существует', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    new_teacher = User(username=username, full_name=full_name, role='teacher', subject=subject)
    new_teacher.set_password(password)
    db.session.add(new_teacher)
    
    db.session.commit()
    flash(f'Учитель {full_name} добавлен! Предмет: {subject}, Логин: {username}, Пароль: {password}', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def admin_delete_user(user_id):
    if current_user.role != 'admin':
        flash('Доступ только для администратора', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Нельзя удалить администратора', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    if user.role == 'student':
        student = Student.query.filter_by(full_name=user.full_name).first()
        if student:
            db.session.delete(student)
    
    db.session.delete(user)
    db.session.commit()
    flash(f'Пользователь {user.full_name} удалён', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin_students')
@login_required
def admin_students():
    if current_user.role != 'admin':
        flash('Доступ только для администратора', 'danger')
        return redirect(url_for('index'))
    
    students = Student.query.all()
    return render_template('admin_students.html', students=students, current_user=current_user)

@app.route('/admin_student/<int:student_id>')
@login_required
def admin_student_detail(student_id):
    if current_user.role != 'admin':
        flash('Доступ только для администратора', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.get_or_404(student_id)
    grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.date.desc()).all()
    return render_template('admin_student_grades.html', student=student, grades=grades, current_user=current_user)

# ==================== СТУДЕНТ ====================

@app.route('/schedule')
@login_required
def schedule_view():
    if current_user.role != 'student':
        flash('Доступ только для учеников', 'danger')
        return redirect(url_for('index'))
    
    week_num = request.args.get('week', type=int)
    current_week = datetime.now().isocalendar()[1]
    if not week_num:
        week_num = current_week
    
    student = Student.query.filter_by(full_name=current_user.full_name).first()
    if not student:
        flash('Профиль не найден', 'danger')
        return redirect(url_for('index'))
    
    schedule = Schedule.query.filter_by(group=current_user.group).all()
    lessons_by_day = {}
    for s in schedule:
        if s.day_of_week not in lessons_by_day:
            lessons_by_day[s.day_of_week] = {}
        lessons_by_day[s.day_of_week][s.lesson_number] = s
    
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    week_offset = (week_num - current_week) * 7
    start_of_week += timedelta(days=week_offset)
    
    dates = [(start_of_week + timedelta(days=i)).strftime('%d.%m') for i in range(7)]
    week_range = f"{start_of_week.strftime('%d.%m.%Y')} - {(start_of_week + timedelta(days=6)).strftime('%d.%m.%Y')}"
    
    return render_template('schedule.html',
                         lessons_by_day=lessons_by_day,
                         dates=dates,
                         week_num=week_num,
                         current_week=current_week,
                         week_range=week_range,
                         group=current_user.group,
                         student_name=current_user.full_name,
                         current_user=current_user)

@app.route('/my_grades')
@login_required
def my_grades():
    if current_user.role != 'student':
        flash('Доступ только для учеников', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.filter_by(full_name=current_user.full_name).first()
    if not student:
        flash('Профиль не найден', 'danger')
        return redirect(url_for('index'))
    
    all_grades = Grade.query.filter_by(student_id=student.id).all()
    
    subjects_grades = {}
    for grade in all_grades:
        if grade.subject not in subjects_grades:
            subjects_grades[grade.subject] = {'1': [], '2': []}
        if grade.quarter == 1:
            subjects_grades[grade.subject]['1'].append(grade.grade)
        else:
            subjects_grades[grade.subject]['2'].append(grade.grade)
    
    result = []
    for subject, quarters in subjects_grades.items():
        q1_grades = quarters['1']
        q2_grades = quarters['2']
        q1_str = ' '.join(format_grade(g) for g in q1_grades) if q1_grades else '-'
        q2_str = ' '.join(format_grade(g) for g in q2_grades) if q2_grades else '-'
        q1_avg = round(sum(q1_grades) / len(q1_grades), 2) if q1_grades else 0
        q2_avg = round(sum(q2_grades) / len(q2_grades), 2) if q2_grades else 0
        result.append({
            'subject': subject,
            'q1_grades': q1_str,
            'q2_grades': q2_str,
            'q1_avg': q1_avg,
            'q2_avg': q2_avg
        })
    
    result.sort(key=lambda x: x['subject'])
    
    return render_template('my_grades.html', grades_table=result, student=student, current_user=current_user)

# ==================== УЧИТЕЛЬ ====================

@app.route('/teacher_journal')
@login_required
def teacher_journal():
    if current_user.role != 'teacher':
        flash('Доступ только для учителей', 'danger')
        return redirect(url_for('index'))
    
    selected_group = request.args.get('group', '')
    groups = ['И-23-2к', 'Э-22-2']
    
    if selected_group and selected_group in groups:
        students = Student.query.filter_by(group=selected_group).all()
    else:
        students = Student.query.all()
        selected_group = 'all'
    
    students_grades = {}
    for student in students:
        grades = Grade.query.filter_by(student_id=student.id, subject=current_user.subject).order_by(Grade.date.desc()).limit(10).all()
        students_grades[student] = grades
    
    return render_template('teacher_journal.html', 
                         students=students,
                         students_grades=students_grades,
                         subject=current_user.subject,
                         groups=groups,
                         selected_group=selected_group,
                         current_user=current_user)

@app.route('/teacher_schedule')
@login_required
def teacher_schedule():
    if current_user.role != 'teacher':
        flash('Доступ только для учителей', 'danger')
        return redirect(url_for('index'))
    
    week_num = request.args.get('week', type=int)
    current_week = datetime.now().isocalendar()[1]
    if not week_num:
        week_num = current_week
    
    schedule = Schedule.query.filter_by(subject=current_user.subject).all()
    
    lessons_by_day = {}
    for s in schedule:
        if s.day_of_week not in lessons_by_day:
            lessons_by_day[s.day_of_week] = {}
        lessons_by_day[s.day_of_week][s.lesson_number] = s
    
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    week_offset = (week_num - current_week) * 7
    start_of_week += timedelta(days=week_offset)
    dates = [(start_of_week + timedelta(days=i)).strftime('%d.%m') for i in range(7)]
    week_range = f"{start_of_week.strftime('%d.%m.%Y')} - {(start_of_week + timedelta(days=6)).strftime('%d.%m.%Y')}"
    
    return render_template('teacher_schedule.html',
                         lessons_by_day=lessons_by_day,
                         dates=dates,
                         week_num=week_num,
                         current_week=current_week,
                         week_range=week_range,
                         subject=current_user.subject,
                         teacher_name=current_user.full_name,
                         current_user=current_user)

@app.route('/teacher_students')
@login_required
def teacher_students():
    if current_user.role != 'teacher':
        flash('Доступ только для учителей', 'danger')
        return redirect(url_for('index'))
    
    students = Student.query.all()
    return render_template('teacher_students.html', students=students, current_user=current_user)

@app.route('/teacher_student/<int:student_id>')
@login_required
def teacher_student_detail(student_id):
    if current_user.role != 'teacher':
        flash('Доступ только для учителей', 'danger')
        return redirect(url_for('index'))
    
    student = Student.query.get_or_404(student_id)
    grades = Grade.query.filter_by(student_id=student_id).order_by(Grade.date.desc()).all()
    return render_template('teacher_student_grades.html', student=student, grades=grades, current_user=current_user)

# ==================== ЧАТ ====================

@app.route('/messages')
@login_required
def messages_list():
    if current_user.role not in ['student', 'teacher']:
        flash('Доступ только для учеников и учителей', 'danger')
        return redirect(url_for('index'))
    
    received = Message.query.filter_by(receiver_id=current_user.id).order_by(Message.created_at.desc()).all()
    sent = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    
    contacts = {}
    
    for msg in received:
        if msg.sender_id not in contacts:
            contact = User.query.get(msg.sender_id)
            if contact:
                unread = Message.query.filter_by(sender_id=msg.sender_id, receiver_id=current_user.id, is_read=False).count()
                contacts[msg.sender_id] = {
                    'user': contact,
                    'last_message': msg.message,
                    'last_date': msg.created_at,
                    'unread': unread
                }
        else:
            if msg.created_at > contacts[msg.sender_id]['last_date']:
                contacts[msg.sender_id]['last_message'] = msg.message
                contacts[msg.sender_id]['last_date'] = msg.created_at
    
    for msg in sent:
        if msg.receiver_id not in contacts:
            contact = User.query.get(msg.receiver_id)
            if contact:
                contacts[msg.receiver_id] = {
                    'user': contact,
                    'last_message': msg.message,
                    'last_date': msg.created_at,
                    'unread': 0
                }
        else:
            if msg.created_at > contacts[msg.receiver_id]['last_date']:
                contacts[msg.receiver_id]['last_message'] = msg.message
                contacts[msg.receiver_id]['last_date'] = msg.created_at
    
    contacts_list = sorted(contacts.values(), key=lambda x: x['last_date'], reverse=True)
    
    return render_template('messages_list.html', contacts=contacts_list, current_user=current_user)

@app.route('/messages/new', methods=['GET', 'POST'])
@login_required
def new_message():
    if current_user.role not in ['student', 'teacher']:
        flash('Доступ только для учеников и учителей', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Обработка отправки сообщения
        receiver_id = request.form.get('receiver_id')
        subject = request.form.get('subject')
        message_text = request.form.get('message')
        
        if not receiver_id or not subject or not message_text:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('new_message'))
        
        receiver = User.query.get(receiver_id)
        if not receiver:
            flash('Получатель не найден', 'danger')
            return redirect(url_for('new_message'))
        
        # Проверка прав
        if current_user.role == 'student' and receiver.role != 'teacher':
            flash('Вы можете писать только учителям', 'danger')
            return redirect(url_for('new_message'))
        if current_user.role == 'teacher' and receiver.role != 'student':
            flash('Вы можете писать только ученикам', 'danger')
            return redirect(url_for('new_message'))
        
        new_msg = Message(
            sender_id=current_user.id,
            receiver_id=receiver_id,
            subject=subject,
            message=message_text
        )
        db.session.add(new_msg)
        db.session.commit()
        flash('Сообщение отправлено!', 'success')
        return redirect(url_for('messages_list'))
    
    # GET запрос - показываем форму выбора получателя
    if current_user.role == 'student':
        recipients = User.query.filter_by(role='teacher').all()
    else:
        recipients = User.query.filter_by(role='student').all()
    
    return render_template('new_message.html', recipients=recipients, current_user=current_user)

@app.route('/messages/send/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_message(user_id):
    receiver = User.query.get_or_404(user_id)
    
    if current_user.role == 'student' and receiver.role != 'teacher':
        flash('Вы можете писать только учителям', 'danger')
        return redirect(url_for('messages_list'))
    
    if current_user.role == 'teacher' and receiver.role != 'student':
        flash('Вы можете писать только ученикам', 'danger')
        return redirect(url_for('messages_list'))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        message_text = request.form.get('message')
        
        if not subject or not message_text:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('send_message', user_id=user_id))
        
        new_msg = Message(
            sender_id=current_user.id,
            receiver_id=user_id,
            subject=subject,
            message=message_text
        )
        db.session.add(new_msg)
        db.session.commit()
        flash('Сообщение отправлено!', 'success')
        return redirect(url_for('messages_list'))
    
    return render_template('send_message.html', receiver=receiver, current_user=current_user)

@app.route('/messages/view/<int:user_id>')
@login_required
def view_messages(user_id):
    other_user = User.query.get_or_404(user_id)
    
    # Отмечаем сообщения как прочитанные
    Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at).all()
    
    return render_template('view_messages.html', other_user=other_user, messages=messages, current_user=current_user)

# ==================== ОЦЕНКИ ====================

@app.route('/add_grade', methods=['POST'])
@login_required
def add_grade():
    if current_user.role != 'teacher':
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('index'))
    
    student_id = request.form.get('student_id')
    grade_value = request.form.get('grade')
    quarter = request.form.get('quarter', 1)
    group = request.form.get('group', '')
    
    grade = Grade(
        student_id=student_id,
        subject=current_user.subject,
        grade=int(grade_value),
        quarter=int(quarter),
        date=datetime.now().strftime('%Y-%m-%d'),
        teacher_name=current_user.full_name
    )
    db.session.add(grade)
    db.session.commit()
    flash('Оценка добавлена!', 'success')
    
    if group:
        return redirect(url_for('teacher_journal', group=group))
    return redirect(url_for('teacher_journal'))

@app.route('/delete_grade/<int:grade_id>')
@login_required
def delete_grade(grade_id):
    grade = Grade.query.get_or_404(grade_id)
    group = request.args.get('group', '')
    
    if current_user.role != 'teacher' or grade.subject != current_user.subject:
        flash('Нет прав', 'danger')
        return redirect(url_for('teacher_journal'))
    
    db.session.delete(grade)
    db.session.commit()
    flash('Оценка удалена', 'success')
    
    if group:
        return redirect(url_for('teacher_journal', group=group))
    return redirect(url_for('teacher_journal'))

if __name__ == '__main__':
    app.run(debug=True)