from extensions import db
from datetime import datetime

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    technologies = db.Column(db.String(500))
    github_link = db.Column(db.String(300))
    live_demo = db.Column(db.String(300))
    start_date = db.Column(db.Date)
    completion_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Planning')
    image_path = db.Column(db.String(255))
    documentation = db.Column(db.String(255))
    certificate = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('ProjectMember', backref='project', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'technologies': self.technologies,
            'github_link': self.github_link,
            'live_demo': self.live_demo,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'status': self.status,
            'image_path': self.image_path,
            'documentation': self.documentation,
            'certificate': self.certificate,
            'members': [m.to_dict() for m in self.members],
        }


class ProjectMember(db.Model):
    __tablename__ = 'project_members'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100))

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'role': self.role}