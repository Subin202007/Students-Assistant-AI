from extensions import db
from datetime import datetime

class Exam(db.Model):
    __tablename__ = 'exams'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # Weekly Test, Internal 1, Internal 2, Internal 3, Semester
    name = db.Column(db.String(150))
    date = db.Column(db.Date)
    max_marks = db.Column(db.Float, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref='exams')
    marks = db.relationship('ExamMark', backref='exam', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'exam_type': self.exam_type,
            'name': self.name,
            'date': self.date.isoformat() if self.date else None,
            'max_marks': self.max_marks,
            'marks': [m.to_dict() for m in self.marks],
        }


class ExamMark(db.Model):
    __tablename__ = 'exam_marks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    obtained_marks = db.Column(db.Float, default=0)

    subject = db.relationship('Subject')

    @property
    def percentage(self):
        if self.exam and self.exam.max_marks:
            return round((self.obtained_marks / self.exam.max_marks) * 100, 2)
        return 0

    def to_dict(self):
        return {
            'id': self.id,
            'exam_id': self.exam_id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'obtained_marks': self.obtained_marks,
            'percentage': self.percentage,
        }


class SemesterResult(db.Model):
    __tablename__ = 'semester_results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    semester = db.Column(db.Integer, nullable=False)
    subject_name = db.Column(db.String(150), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(5))
    grade_point = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'semester': self.semester,
            'subject_name': self.subject_name,
            'credits': self.credits,
            'grade': self.grade,
            'grade_point': self.grade_point,
        }