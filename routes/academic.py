from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models.academic import Subject, AcademicRecord

academic_bp = Blueprint('academic', __name__)


@academic_bp.route('/academics')
@login_required
def academics_page():
    return render_template('academic.html')


@academic_bp.route('/api/subjects', methods=['GET'])
@login_required
def get_subjects():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return jsonify([s.to_dict() for s in subjects])


@academic_bp.route('/api/subjects', methods=['POST'])
@login_required
def create_subject():
    data = request.json
    subject = Subject(
        user_id=current_user.id,
        code=data.get('code', ''),
        name=data.get('name', ''),
        faculty=data.get('faculty', ''),
        credits=int(data.get('credits', 0)),
        semester=int(data.get('semester', current_user.semester or 1)),
    )
    db.session.add(subject)
    db.session.commit()
    return jsonify(subject.to_dict()), 201


@academic_bp.route('/api/subjects/<int:id>', methods=['PUT'])
@login_required
def update_subject(id):
    subject = Subject.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.json
    subject.code = data.get('code', subject.code)
    subject.name = data.get('name', subject.name)
    subject.faculty = data.get('faculty', subject.faculty)
    subject.credits = int(data.get('credits', subject.credits))
    subject.semester = int(data.get('semester', subject.semester))
    db.session.commit()
    return jsonify(subject.to_dict())


@academic_bp.route('/api/subjects/<int:id>', methods=['DELETE'])
@login_required
def delete_subject(id):
    subject = Subject.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(subject)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@academic_bp.route('/api/academic-records', methods=['GET'])
@login_required
def get_records():
    records = AcademicRecord.query.filter_by(user_id=current_user.id).all()
    return jsonify([r.to_dict() for r in records])


@academic_bp.route('/api/academic-records', methods=['POST'])
@login_required
def create_record():
    data = request.json
    record = AcademicRecord(
        user_id=current_user.id,
        subject_id=data.get('subject_id'),
        internal_marks=float(data.get('internal_marks', 0)),
        assignment_marks=float(data.get('assignment_marks', 0)),
        practical_marks=float(data.get('practical_marks', 0)),
        university_marks=float(data.get('university_marks', 0)),
        max_marks=float(data.get('max_marks', 100)),
        grade=data.get('grade', ''),
        grade_point=float(data.get('grade_point', 0)),
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(record.to_dict()), 201


@academic_bp.route('/api/academic-records/<int:id>', methods=['PUT'])
@login_required
def update_record(id):
    record = AcademicRecord.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.json
    for field in ['internal_marks', 'assignment_marks', 'practical_marks', 'university_marks', 'max_marks', 'grade_point']:
        if field in data:
            setattr(record, field, float(data[field]))
    if 'grade' in data:
        record.grade = data['grade']
    if 'subject_id' in data:
        record.subject_id = data['subject_id']
    db.session.commit()
    return jsonify(record.to_dict())


@academic_bp.route('/api/academic-records/<int:id>', methods=['DELETE'])
@login_required
def delete_record(id):
    record = AcademicRecord.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Deleted'})