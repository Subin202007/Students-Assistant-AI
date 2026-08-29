from extensions import db
from datetime import datetime

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    title = db.Column(db.String(200), nullable=False)
    unit = db.Column(db.Integer)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    tags = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subject = db.relationship('Subject', backref='notes')

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else 'General',
            'title': self.title,
            'unit': self.unit,
            'description': self.description,
            'content': self.content,
            'file_path': self.file_path,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }