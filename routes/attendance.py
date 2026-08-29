from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models.attendance import Attendance
from models.academic import Subject

attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/attendance')
@login_required
def attendance_page():
    return render_template('attendance.html')


@attendance_bp.route('/api/attendance', methods=['GET'])
@login_required
def get_attendance():
    records = Attendance.query.filter_by(user_id=current_user.id).all()
    data = [r.to_dict() for r in records]
    total_attended = sum(r.classes_attended for r in records)
    total_classes = sum(r.total_classes for r in records)
    overall = round((total_attended / total_classes) * 100, 2) if total_classes > 0 else 0
    return jsonify({'records': data, 'overall': overall})


@attendance_bp.route('/api/attendance', methods=['POST'])
@login_required
def create_attendance():
    data = request.json
    record = Attendance(
        user_id=current_user.id,
        subject_id=data.get('subject_id'),
        total_classes=int(data.get('total_classes', 0)),
        classes_attended=int(data.get('classes_attended', 0)),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@attendance_bp.route('/api/attendance/<int:id>', methods=['PUT'])
@login_required
def update_attendance(id):
    record = Attendance.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.json
    if 'subject_id' in data:
        record.subject_id = data['subject_id']
    if 'total_classes' in data:
        record.total_classes = int(data['total_classes'])
    if 'classes_attended' in data:
        record.classes_attended = int(data['classes_attended'])
    db.session.commit()
    return jsonify(record.to_dict())


@attendance_bp.route('/api/attendance/<int:id>', methods=['DELETE'])
@login_required
def delete_attendance(id):
    record = Attendance.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@attendance_bp.route('/api/attendance/mark', methods=['POST'])
@login_required
def mark_attendance():
    """Increment attendance for a subject."""
    data = request.json
    subject_id = data.get('subject_id')
    present = data.get('present', True)
    record = Attendance.query.filter_by(user_id=current_user.id, subject_id=subject_id).first()
    if not record:
        record = Attendance(user_id=current_user.id, subject_id=subject_id, total_classes=0, classes_attended=0)
        db.session.add(record)
    record.total_classes += 1
    if present:
        record.classes_attended += 1
    db.session.commit()
    return jsonify(record.to_dict())