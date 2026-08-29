from models.academic import Subject
from models.attendance import Attendance
from models.fees import Fee
from models.assignments import Assignment
from models.projects import Project
from models.exams import SemesterResult
from services.cgpa_service import calculate_cgpa


def get_dashboard_stats(user_id):
    """Get all dashboard statistics for a user."""
    subjects = Subject.query.filter_by(user_id=user_id).all()
    attendance_records = Attendance.query.filter_by(user_id=user_id).all()
    fees = Fee.query.filter_by(user_id=user_id).all()
    assignments = Assignment.query.filter_by(user_id=user_id).all()
    projects = Project.query.filter_by(user_id=user_id).all()
    all_results = SemesterResult.query.filter_by(user_id=user_id).all()

    # Attendance
    total_attended = sum(r.classes_attended for r in attendance_records)
    total_classes = sum(r.total_classes for r in attendance_records)
    attendance_pct = round((total_attended / total_classes) * 100, 2) if total_classes > 0 else 0

    # Fees
    total_fee = sum(f.total_amount for f in fees)
    paid_fee = sum(f.paid_amount for f in fees)
    fee_balance = total_fee - paid_fee

    # Assignments
    pending_assignments = [a for a in assignments if a.status in ['Pending', 'In Progress']]
    completed_assignments = [a for a in assignments if a.status in ['Completed', 'Submitted']]
    overdue_assignments = [a for a in assignments if a.is_overdue]

    # Projects
    completed_projects = [p for p in projects if p.status == 'Completed']

    # CGPA
    cgpa = calculate_cgpa(all_results)

    # Subject-wise performance (from attendance)
    subject_attendance = []
    for r in attendance_records:
        subject_attendance.append({
            'name': r.subject.name if r.subject else 'Unknown',
            'percentage': r.percentage,
            'status': r.status,
        })

    return {
        'total_subjects': len(subjects),
        'attendance_percentage': attendance_pct,
        'current_cgpa': cgpa,
        'pending_assignments': len(pending_assignments),
        'completed_assignments': len(completed_assignments),
        'overdue_assignments': len(overdue_assignments),
        'completed_projects': len(completed_projects),
        'total_projects': len(projects),
        'fee_balance': fee_balance,
        'total_fee': total_fee,
        'paid_fee': paid_fee,
        'subject_attendance': subject_attendance,
        'pending_assignment_list': [
            {'id': a.id, 'title': a.title, 'due_date': a.due_date.isoformat() if a.due_date else None, 'subject': a.subject.name if a.subject else ''}
            for a in pending_assignments[:5]
        ],
    }