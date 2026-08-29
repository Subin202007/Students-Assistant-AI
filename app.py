import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, login_manager
from models.user import User  # <-- Added this import


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure upload directories exist
    upload_dirs = ['notes', 'assignments', 'projects', 'profile', 'receipts', 'certificates']
    for d in upload_dirs:
        path = os.path.join(app.config['UPLOAD_FOLDER'], d)
        os.makedirs(path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # ✅ ADD THIS: Tell Flask-Login how to load a user
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.academic import academic_bp
    from routes.attendance import attendance_bp
    from routes.fees import fees_bp
    from routes.notes import notes_bp
    from routes.assignments import assignments_bp
    from routes.projects import projects_bp
    from routes.exams import exams_bp
    from routes.cgpa import cgpa_bp
    from routes.resume import resume_bp
    from routes.ai import ai_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(fees_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(assignments_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(exams_bp)
    app.register_blueprint(cgpa_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(profile_bp)

    @app.route('/')
    def index():
        from flask_login import current_user
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.dashboard'))
        return redirect(url_for('auth.landing'))

    # Create tables and seed demo data
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            seed_demo_data()

    return app


def seed_demo_data():
    from models.academic import Subject
    from models.attendance import Attendance
    from models.fees import Fee
    from models.assignments import Assignment
    from models.projects import Project
    from models.exams import Exam, ExamMark
    from models.notes import Note
    from werkzeug.security import generate_password_hash
    from datetime import datetime, timedelta

    demo = User(
        full_name='Demo Student', email='demo@student.com', phone='9876543210',
        password_hash=generate_password_hash('demo123'), college='Demo University',
        department='Computer Science', register_number='DEMO2024001',
        academic_year='2024-2025', semester=4
    )
    db.session.add(demo)
    db.session.commit()

    subjects_data = [
        ('CS301', 'Data Structures', 'Dr. Smith', 4, 4),
        ('CS302', 'Database Management', 'Dr. Johnson', 4, 4),
        ('CS303', 'Operating Systems', 'Dr. Williams', 3, 4),
        ('CS304', 'Computer Networks', 'Dr. Brown', 3, 4),
        ('MA301', 'Discrete Mathematics', 'Dr. Davis', 4, 4),
    ]
    subjects = []
    for code, name, faculty, credits, sem in subjects_data:
        s = Subject(user_id=demo.id, code=code, name=name, faculty=faculty, credits=credits, semester=sem)
        db.session.add(s)
        subjects.append(s)
    db.session.commit()

    for i, s in enumerate(subjects):
        total = 40 + i * 2
        attended = int(total * (0.92 - i * 0.04))
        db.session.add(Attendance(user_id=demo.id, subject_id=s.id, total_classes=total, classes_attended=attended))
    db.session.commit()

    db.session.add(Fee(user_id=demo.id, fee_type='Tuition Fee', total_amount=75000, paid_amount=62500, payment_date=datetime.now().date(), payment_method='Online', reference_number='TXN123456', status='Partial'))
    db.session.commit()

    for i in range(3):
        db.session.add(Assignment(user_id=demo.id, subject_id=subjects[i].id, title=f'Assignment {i+1}', description=f'Chapter {i+1}', faculty=subjects[i].faculty, assigned_date=datetime.now().date() - timedelta(days=7), due_date=datetime.now().date() + timedelta(days=3-i), status=['Pending','In Progress','Completed'][i]))
    db.session.commit()

    db.session.add(Project(user_id=demo.id, title='AI Medical Assistant', description='AI diagnosis system', technologies='Python, Flask, TensorFlow', github_link='https://github.com/demo', live_demo='https://demo.com', start_date=datetime.now().date()-timedelta(days=60), completion_date=datetime.now().date()-timedelta(days=5), status='Completed'))
    db.session.commit()

    for s in subjects[:3]:
        exam = Exam(user_id=demo.id, subject_id=s.id, exam_type='Internal 1', date=datetime.now().date()-timedelta(days=20), max_marks=50)
        db.session.add(exam)
        db.session.commit()
        db.session.add(ExamMark(user_id=demo.id, exam_id=exam.id, subject_id=s.id, obtained_marks=35+subjects.index(s)*3))
    db.session.commit()

    db.session.add(Note(user_id=demo.id, subject_id=subjects[0].id, title='Linked Lists', unit=1, description='Notes', content='A linked list is...'))
    db.session.commit()
    print("✅ Demo data seeded successfully!")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)