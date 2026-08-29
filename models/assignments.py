from extensions import db
from datetime import datetime

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    faculty = db.Column(db.String(150))
    assigned_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending')
    submission_file = db.Column(db.String(255))
    marks = db.Column(db.Float)
    max_marks = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref='assignments')

    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['Completed', 'Submitted']:
            return self.due_date < datetime.now().date()
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else 'General',
            'title': self.title,
            'description': self.description,
            'faculty': self.faculty,
            'assigned_date': self.assigned_date.isoformat() if self.assigned_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'submission_file': self.submission_file,
            'marks': self.marks,
            'max_marks': self.max_marks,
            'is_overdue': self.is_overdue,
        }