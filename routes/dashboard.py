from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models.academic import Subject
from models.attendance import Attendance
from models.fees import Fee
from models.assignments import Assignment
from models.projects import Project
from models.exams import Exam, ExamMark, SemesterResult
from models.notes import Note
from services.analytics_service import get_dashboard_stats

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@dashboard_bp.route('/api/dashboard')
@login_required
def dashboard_data():
    stats = get_dashboard_stats(current_user.id)
    return jsonify(stats)