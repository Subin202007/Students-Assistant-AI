import os
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from extensions import db
from models.projects import Project, ProjectMember
from werkzeug.utils import secure_filename
from datetime import datetime

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('/projects')
@login_required
def projects_page():
    return render_template('projects.html')


@projects_bp.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return jsonify([p.to_dict() for p in projects])


@projects_bp.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.form if request.form else request.json
    image_path = None
    if request.files.get('image'):
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(f"proj_{datetime.now().timestamp()}_{file.filename}")
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', filename)
            file.save(path)
            image_path = f"projects/{filename}"

    project = Project(
        user_id=current_user.id,
        title=data.get('title', ''),
        description=data.get('description', ''),
        technologies=data.get('technologies', ''),
        github_link=data.get('github_link', ''),
        live_demo=data.get('live_demo', ''),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
        completion_date=datetime.strptime(data['completion_date'], '%Y-%m-%d').date() if data.get('completion_date') else None,
        status=data.get('status', 'Planning'),
        image_path=image_path,
    )
    db.session.add(project)
    db.session.commit()

    # Add members
    members_str = data.get('members', '')
    if members_str:
        for m in members_str.split(','):
            m = m.strip()
            if m:
                member = ProjectMember(project_id=project.id, name=m)
                db.session.add(member)
        db.session.commit()

    return jsonify(project.to_dict()), 201


@projects_bp.route('/api/projects/<int:id>', methods=['PUT'])
@login_required
def update_project(id):
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.form if request.form else request.json
    for field in ['title', 'description', 'technologies', 'github_link', 'live_demo', 'status']:
        if field in data:
            setattr(project, field, data[field])
    if data.get('start_date'):
        project.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
    if data.get('completion_date'):
        project.completion_date = datetime.strptime(data['completion_date'], '%Y-%m-%d').date()

    if request.files.get('image'):
        file = request.files['image']
        if file and file.filename:
            filename = secure_filename(f"proj_{datetime.now().timestamp()}_{file.filename}")
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', filename)
            file.save(path)
            project.image_path = f"projects/{filename}"

    db.session.commit()
    return jsonify(project.to_dict())


@projects_bp.route('/api/projects/<int:id>', methods=['DELETE'])
@login_required
def delete_project(id):
    project = Project.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(project)
    db.session.commit()
    return jsonify({'message': 'Deleted'})