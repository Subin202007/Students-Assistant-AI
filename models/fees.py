from extensions import db
from datetime import datetime

class Fee(db.Model):
    __tablename__ = 'fees'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fee_type = db.Column(db.String(100), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0)
    paid_amount = db.Column(db.Float, default=0)
    payment_date = db.Column(db.Date)
    payment_method = db.Column(db.String(50))
    reference_number = db.Column(db.String(100))
    receipt_file = db.Column(db.String(255))
    status = db.Column(db.String(20), default='Pending')  # Pending, Partial, Paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def remaining(self):
        return self.total_amount - self.paid_amount

    def to_dict(self):
        return {
            'id': self.id,
            'fee_type': self.fee_type,
            'total_amount': self.total_amount,
            'paid_amount': self.paid_amount,
            'remaining': self.remaining,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'receipt_file': self.receipt_file,
            'status': self.status,
        }


class FeePayment(db.Model):
    __tablename__ = 'fee_payments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fee_id = db.Column(db.Integer, db.ForeignKey('fees.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow)
    payment_method = db.Column(db.String(50))
    reference_number = db.Column(db.String(100))
    receipt_file = db.Column(db.String(255))

    fee = db.relationship('Fee', backref='payments')

    def to_dict(self):
        return {
            'id': self.id,
            'fee_id': self.fee_id,
            'fee_type': self.fee.fee_type if self.fee else '',
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
        }