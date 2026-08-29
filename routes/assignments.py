import os
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from extensions import db
from models.assignments import Assignment
from werkzeug.utils import secure_filename
from datetime import datetime

assignments_bp = Blueprint('assignments', __name__)


@assignments_bp.route('/assignments')
@login_required
def assignments_page():
    return render_template('assignments.html')


@assignments_bp.route('/api/assignments', methods=['GET'])
@login_required
def get_assignments():
    status = request.args.get('status')
    query = Assignment.query.filter_by(user_id=current_user.id)
    if status:
        query = query.filter_by(status=status)
    assignments = query.order_by(Assignment.due_date.asc()).all()
    return jsonify([a.to_dict() for a in assignments])


@assignments_bp.route('/api/assignments', methods=['POST'])
@login_required
def create_assignment():
    submission_file = None
    if request.files.get('submission'):
        file = request.files['submission']
        if file and file.filename:
            filename = secure_filename(f"assign_{datetime.now().timestamp()}_{file.filename}")
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'assignments', filename)
            file.save(path)
            submission_file = f"assignments/{filename}"

    data = request.form if request.form else request.json
    assignment = Assignment(
        user_id=current_user.id,
        subject_id=data.get('subject_id') or None,
        title=data.get('title', ''),
        description=data.get('description', ''),
        faculty=data.get('faculty', ''),
        assigned_date=datetime.strptime(data['assigned_date'], '%Y-%m-%d').date() if data.get('assigned_date') else datetime.now().date(),
        due_date=datetime.strptime(data['due_date'], '%Y-%m-%d').date() if data.get('due_date') else None,
        status=data.get('status', 'Pending'),
        submission_file=submission_file,
        marks=float(data.get('marks', 0)) if data.get('marks') else None,
        max_marks=float(data.get('max_marks', 0)) if data.get('max_marks') else None,
    )
    db.session.add(assignment)
    db.session.commit()
    return jsonify(assignment.to_dict()), 201


@assignments_bp.route('/api/assignments/<int:id>', methods=['PUT'])
@login_required
def update_assignment(id):
    assignment = Assignment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.form if request.form else request.json
    for field in ['title', 'description', 'faculty', 'status']:
        if field in data:
            setattr(assignment, field, data[field])
    if data.get('subject_id'):
        assignment.subject_id = int(data['subject_id'])
    if data.get('due_date'):
        assignment.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
    if data.get('assigned_date'):
        assignment.assigned_date = datetime.strptime(data['assigned_date'], '%Y-%m-%d').date()
    if data.get('marks'):
        assignment.marks = float(data['marks'])
    if data.get('max_marks'):
        assignment.max_marks = float(data['max_marks'])

    if request.files.get('submission'):
        file = request.files['submission']
        if file and file.filename:
            filename = secure_filename(f"assign_{datetime.now().timestamp()}_{file.filename}")
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'assignments', filename)
            file.save(path)
            assignment.submission_file = f"assignments/{filename}"

    db.session.commit()
    return jsonify(assignment.to_dict())


@assignments_bp.route('/api/assignments/<int:id>', methods=['DELETE'])
@login_required
def delete_assignment(id):
    assignment = Assignment.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({'message': 'Deleted'})