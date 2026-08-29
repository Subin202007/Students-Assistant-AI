import os
from flask import Blueprint, request, jsonify, render_template, current_app, send_from_directory
from flask_login import login_required, current_user
from extensions import db
from models.fees import Fee, FeePayment
from werkzeug.utils import secure_filename
from datetime import datetime

fees_bp = Blueprint('fees', __name__)


@fees_bp.route('/fees')
@login_required
def fees_page():
    return render_template('fees.html')


@fees_bp.route('/api/fees', methods=['GET'])
@login_required
def get_fees():
    fees = Fee.query.filter_by(user_id=current_user.id).all()
    data = [f.to_dict() for f in fees]
    total = sum(f.total_amount for f in fees)
    paid = sum(f.paid_amount for f in fees)
    return jsonify({'fees': data, 'total': total, 'paid': paid, 'remaining': total - paid})


@fees_bp.route('/api/fees', methods=['POST'])
@login_required
def create_fee():
    data = request.form if request.files else request.json
    receipt_file = None
    if request.files.get('receipt'):
        file = request.files['receipt']
        if file and file.filename:
            filename = secure_filename(f"fee_{datetime.now().timestamp()}_{file.filename}")
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'receipts', filename)
            file.save(path)
            receipt_file = f"receipts/{filename}"

    fee = Fee(
        user_id=current_user.id,
        fee_type=data.get('fee_type', 'Tuition'),
        total_amount=float(data.get('total_amount', 0)),
        paid_amount=float(data.get('paid_amount', 0)),
        payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date() if data.get('payment_date') else datetime.now().date(),
        payment_method=data.get('payment_method', ''),
        reference_number=data.get('reference_number', ''),
        receipt_file=receipt_file,
        status=data.get('status', 'Pending'),
    )
    db.session.add(fee)
    db.session.commit()
    return jsonify(fee.to_dict()), 201


@fees_bp.route('/api/fees/<int:id>', methods=['PUT'])
@login_required
def update_fee(id):
    fee = Fee.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.json
    for field in ['fee_type', 'payment_method', 'reference_number', 'status']:
        if field in data:
            setattr(fee, field, data[field])
    for field in ['total_amount', 'paid_amount']:
        if field in data:
            setattr(fee, field, float(data[field]))
    if 'payment_date' in data and data['payment_date']:
        fee.payment_date = datetime.strptime(data['payment_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(fee.to_dict())


@fees_bp.route('/api/fees/<int:id>', methods=['DELETE'])
@login_required
def delete_fee(id):
    fee = Fee.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(fee)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@fees_bp.route('/api/fees/payments', methods=['GET'])
@login_required
def get_payments():
    payments = FeePayment.query.filter_by(user_id=current_user.id).all()
    return jsonify([p.to_dict() for p in payments])


@fees_bp.route('/api/fees/payments', methods=['POST'])
@login_required
def create_payment():
    data = request.json
    payment = FeePayment(
        user_id=current_user.id,
        fee_id=data.get('fee_id'),
        amount=float(data.get('amount', 0)),
        payment_method=data.get('payment_method', ''),
        reference_number=data.get('reference_number', ''),
        payment_date=datetime.strptime(data['payment_date'], '%Y-%m-%d').date() if data.get('payment_date') else datetime.now().date(),
    )
    db.session.add(payment)
    # Update fee paid amount
    fee = Fee.query.filter_by(id=payment.fee_id, user_id=current_user.id).first()
    if fee:
        fee.paid_amount += payment.amount
        fee.status = 'Paid' if fee.paid_amount >= fee.total_amount else 'Partial'
    db.session.commit()
    return jsonify(payment.to_dict()), 201