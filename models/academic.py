from extensions import db
from datetime import datetime

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    faculty = db.Column(db.String(150))
    credits = db.Column(db.Integer, default=0)
    semester = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'faculty': self.faculty,
            'credits': self.credits,
            'semester': self.semester,
        }


class AcademicRecord(db.Model):
    __tablename__ = 'academic_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    internal_marks = db.Column(db.Float, default=0)
    assignment_marks = db.Column(db.Float, default=0)
    practical_marks = db.Column(db.Float, default=0)
    university_marks = db.Column(db.Float, default=0)
    max_marks = db.Column(db.Float, default=100)
    grade = db.Column(db.String(5))
    grade_point = db.Column(db.Float, default=0)

    subject = db.relationship('Subject', backref='academic_records')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'internal_marks': self.internal_marks,
            'assignment_marks': self.assignment_marks,
            'practical_marks': self.practical_marks,
            'university_marks': self.university_marks,
            'max_marks': self.max_marks,
            'grade': self.grade,
            'grade_point': self.grade_point,
        }