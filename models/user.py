from extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    college = db.Column(db.String(200))
    department = db.Column(db.String(150))
    register_number = db.Column(db.String(50))
    academic_year = db.Column(db.String(20))
    semester = db.Column(db.Integer, default=1)
    profile_photo = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    subjects = db.relationship('Subject', backref='user', lazy=True, cascade='all, delete-orphan')
    attendance_records = db.relationship('Attendance', backref='user', lazy=True, cascade='all, delete-orphan')
    fees = db.relationship('Fee', backref='user', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', backref='user', lazy=True, cascade='all, delete-orphan')
    projects = db.relationship('Project', backref='user', lazy=True, cascade='all, delete-orphan')
    exams = db.relationship('Exam', backref='user', lazy=True, cascade='all, delete-orphan')
    exam_marks = db.relationship('ExamMark', backref='user', lazy=True, cascade='all, delete-orphan')
    semester_results = db.relationship('SemesterResult', backref='user', lazy=True, cascade='all, delete-orphan')
    resume_profile = db.relationship('ResumeProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    certifications = db.relationship('Certification', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='user', lazy=True, cascade='all, delete-orphan')
    chat_sessions = db.relationship('ChatSession', backref='user', lazy=True, cascade='all, delete-orphan')
    study_materials = db.relationship('StudyMaterial', backref='user', lazy=True, cascade='all, delete-orphan')
    calendar_events = db.relationship('CalendarEvent', backref='user', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'college': self.college,
            'department': self.department,
            'register_number': self.register_number,
            'academic_year': self.academic_year,
            'semester': self.semester,
            'profile_photo': self.profile_photo,
        }