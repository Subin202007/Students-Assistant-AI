from extensions import db
from datetime import datetime

class ResumeProfile(db.Model):
    __tablename__ = 'resume_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    linkedin = db.Column(db.String(300))
    github = db.Column(db.String(300))
    portfolio = db.Column(db.String(300))
    location = db.Column(db.String(200))
    skills = db.Column(db.Text)  # JSON string
    summary = db.Column(db.Text)
    template = db.Column(db.String(50), default='modern')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'linkedin': self.linkedin,
            'github': self.github,
            'portfolio': self.portfolio,
            'location': self.location,
            'skills': self.skills,
            'summary': self.summary,
            'template': self.template,
        }


class Certification(db.Model):
    __tablename__ = 'certifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    issuer = db.Column(db.String(200))
    date = db.Column(db.Date)
    credential_id = db.Column(db.String(100))
    file_path = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'issuer': self.issuer,
            'date': self.date.isoformat() if self.date else None,
            'credential_id': self.credential_id,
        }


class Achievement(db.Model):
    __tablename__ = 'achievements'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.Date)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
        }