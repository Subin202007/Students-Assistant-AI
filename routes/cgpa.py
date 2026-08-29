from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models.exams import SemesterResult
from services.cgpa_service import calculate_gpa, calculate_cgpa

cgpa_bp = Blueprint('cgpa', __name__)


@cgpa_bp.route('/cgpa')
@login_required
def cgpa_page():
    return render_template('cgpa.html')


@cgpa_bp.route('/api/cgpa/semesters', methods=['GET'])
@login_required
def get_semester_results():
    results = SemesterResult.query.filter_by(user_id=current_user.id).order_by(SemesterResult.semester).all()
    # Group by semester
    semesters = {}
    for r in results:
        if r.semester not in semesters:
            semesters[r.semester] = []
        semesters[r.semester].append(r.to_dict())
    return jsonify(semesters)


@cgpa_bp.route('/api/cgpa/calculate', methods=['POST'])
@login_required
def calculate():
    data = request.json
    semester = int(data.get('semester', current_user.semester or 1))
    subjects = data.get('subjects', [])

    # Delete existing results for this semester
    SemesterResult.query.filter_by(user_id=current_user.id, semester=semester).delete()

    total_points = 0
    total_credits = 0
    for s in subjects:
        credits = int(s.get('credits', 0))
        grade_point = float(s.get('grade_point', 0))
        result = SemesterResult(
            user_id=current_user.id,
            semester=semester,
            subject_name=s.get('subject_name', ''),
            credits=credits,
            grade=s.get('grade', ''),
            grade_point=grade_point,
        )
        db.session.add(result)
        total_points += credits * grade_point
        total_credits += credits

    db.session.commit()

    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0

    # Calculate overall CGPA
    all_results = SemesterResult.query.filter_by(user_id=current_user.id).all()
    cgpa = calculate_cgpa(all_results)

    return jsonify({
        'semester': semester,
        'gpa': gpa,
        'cgpa': cgpa,
        'total_credits': total_credits,
    })


@cgpa_bp.route('/api/cgpa/overall', methods=['GET'])
@login_required
def overall_cgpa():
    all_results = SemesterResult.query.filter_by(user_id=current_user.id).all()
    semesters = {}
    for r in all_results:
        if r.semester not in semesters:
            semesters[r.semester] = []
        semesters[r.semester].append(r)

    semester_gpas = []
    for sem in sorted(semesters.keys()):
        gpa = calculate_gpa(semesters[sem])
        semester_gpas.append({'semester': sem, 'gpa': gpa})

    cgpa = calculate_cgpa(all_results)
    return jsonify({'semester_gpas': semester_gpas, 'cgpa': cgpa})


@cgpa_bp.route('/api/cgpa/semester/<int:semester>', methods=['DELETE'])
@login_required
def delete_semester(semester):
    SemesterResult.query.filter_by(user_id=current_user.id, semester=semester).delete()
    db.session.commit()
    return jsonify({'message': 'Deleted'})