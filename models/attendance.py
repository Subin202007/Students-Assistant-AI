from extensions import db
from datetime import datetime

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    total_classes = db.Column(db.Integer, default=0)
    classes_attended = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subject = db.relationship('Subject', backref='attendance_records')

    @property
    def classes_absent(self):
        return self.total_classes - self.classes_attended

    @property
    def percentage(self):
        if self.total_classes == 0:
            return 0
        return round((self.classes_attended / self.total_classes) * 100, 2)

    @property
    def status(self):
        p = self.percentage
        if p >= 90:
            return 'Excellent'
        elif p >= 75:
            return 'Good'
        elif p >= 65:
            return 'Warning'
        else:
            return 'Critical'

    def classes_needed_for_target(self, target=75):
        """Calculate classes needed to reach target attendance."""
        if self.total_classes == 0:
            return target
        current = self.classes_attended
        total = self.total_classes
        # Solve: (current + x) / (total + x) >= target/100
        # x >= (target*total - 100*current) / (100 - target)
        needed = (target * total - 100 * current) / (100 - target)
        return max(0, int(needed) + (1 if needed != int(needed) else 0))

    def to_dict(self):
        return {
            'id': self.id,
            'subject_id': self.subject_id,
            'subject_name': self.subject.name if self.subject else '',
            'subject_code': self.subject.code if self.subject else '',
            'total_classes': self.total_classes,
            'classes_attended': self.classes_attended,
            'classes_absent': self.classes_absent,
            'percentage': self.percentage,
            'status': self.status,
            'classes_needed_75': self.classes_needed_for_target(75),
        }