from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models.exams import Exam, ExamMark, SemesterResult
from models.academic import Subject
from datetime import datetime

exams_bp = Blueprint('exams', __name__)


@exams_bp.route('/exams')
@login_required
def exams_page():
    return render_template('exams.html')


@exams_bp.route('/api/exams', methods=['GET'])
@login_required
def get_exams():
    exams = Exam.query.filter_by(user_id=current_user.id).order_by(Exam.date.desc()).all()
    return jsonify([e.to_dict() for e in exams])


@exams_bp.route('/api/exams', methods=['POST'])
@login_required
def create_exam():
    data = request.json
    exam = Exam(
        user_id=current_user.id,
        subject_id=data.get('subject_id'),
        exam_type=data.get('exam_type', 'Internal 1'),
        name=data.get('name', ''),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.now().date(),
        max_marks=float(data.get('max_marks', 100)),
    )
    db.session.add(exam)
    db.session.commit()

    if data.get('obtained_marks') is not None:
        mark = ExamMark(
            user_id=current_user.id,
            exam_id=exam.id,
            subject_id=exam.subject_id,
            obtained_marks=float(data['obtained_marks']),
        )
        db.session.add(mark)
        db.session.commit()

    return jsonify(exam.to_dict()), 201


@exams_bp.route('/api/exams/<int:id>', methods=['PUT'])
@login_required
def update_exam(id):
    exam = Exam.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.json
    for field in ['exam_type', 'name']:
        if field in data:
            setattr(exam, field, data[field])
    if data.get('subject_id'):
        exam.subject_id = data['subject_id']
    if data.get('max_marks'):
        exam.max_marks = float(data['max_marks'])
    if data.get('date'):
        exam.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(exam.to_dict())


@exams_bp.route('/api/exams/<int:id>', methods=['DELETE'])
@login_required
def delete_exam(id):
    exam = Exam.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(exam)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@exams_bp.route('/api/exams/analytics', methods=['GET'])
@login_required
def exam_analytics():
    marks = ExamMark.query.filter_by(user_id=current_user.id).all()
    exams = Exam.query.filter_by(user_id=current_user.id).all()

    subject_stats = {}
    for m in marks:
        exam = next((e for e in exams if e.id == m.exam_id), None)
        if not exam:
            continue
        sname = m.subject.name if m.subject else 'Unknown'
        if sname not in subject_stats:
            subject_stats[sname] = {'marks': [], 'max': 0}
        subject_stats[sname]['marks'].append(m.obtained_marks)
        subject_stats[sname]['max'] = max(subject_stats[sname]['max'], exam.max_marks)

    analytics = []
    for sname, stats in subject_stats.items():
        avg = sum(stats['marks']) / len(stats['marks']) if stats['marks'] else 0
        analytics.append({
            'subject': sname,
            'average': round(avg, 2),
            'highest': max(stats['marks']) if stats['marks'] else 0,
            'lowest': min(stats['marks']) if stats['marks'] else 0,
            'max_marks': stats['max'],
            'attempts': len(stats['marks']),
        })

    return jsonify({
        'analytics': analytics,
        'total_exams': len(exams),
        'total_marks_entries': len(marks),
    })


@exams_bp.route('/api/exams/marks', methods=['POST'])
@login_required
def add_mark():
    data = request.json
    mark = ExamMark(
        user_id=current_user.id,
        exam_id=data.get('exam_id'),
        subject_id=data.get('subject_id'),
        obtained_marks=float(data.get('obtained_marks', 0)),
    )
    db.session.add(mark)
    db.session.commit()
    return jsonify(mark.to_dict()), 201