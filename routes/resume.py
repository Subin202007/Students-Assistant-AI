from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models.resume import ResumeProfile, Certification, Achievement
from models.projects import Project
from services.resume_service import generate_resume_content
from datetime import datetime

resume_bp = Blueprint('resume', __name__)


@resume_bp.route('/resume')
@login_required
def resume_page():
    return render_template('resume.html')


@resume_bp.route('/api/resume/profile', methods=['GET'])
@login_required
def get_resume_profile():
    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first()
    certs = Certification.query.filter_by(user_id=current_user.id).all()
    achievements = Achievement.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id, status='Completed').all()
    return jsonify({
        'profile': profile.to_dict() if profile else None,
        'certifications': [c.to_dict() for c in certs],
        'achievements': [a.to_dict() for a in achievements],
        'projects': [p.to_dict() for p in projects],
        'user': current_user.to_dict(),
    })


@resume_bp.route('/api/resume/profile', methods=['POST', 'PUT'])
@login_required
def save_resume_profile():
    data = request.json
    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = ResumeProfile(user_id=current_user.id)
        db.session.add(profile)

    for field in ['linkedin', 'github', 'portfolio', 'location', 'skills', 'summary', 'template']:
        if field in data:
            setattr(profile, field, data[field])

    db.session.commit()
    return jsonify(profile.to_dict())


@resume_bp.route('/api/resume/certifications', methods=['POST'])
@login_required
def add_certification():
    data = request.json
    cert = Certification(
        user_id=current_user.id,
        title=data.get('title', ''),
        issuer=data.get('issuer', ''),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else None,
        credential_id=data.get('credential_id', ''),
    )
    db.session.add(cert)
    db.session.commit()
    return jsonify(cert.to_dict()), 201


@resume_bp.route('/api/resume/certifications/<int:id>', methods=['DELETE'])
@login_required
def delete_certification(id):
    cert = Certification.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(cert)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@resume_bp.route('/api/resume/achievements', methods=['POST'])
@login_required
def add_achievement():
    data = request.json
    ach = Achievement(
        user_id=current_user.id,
        title=data.get('title', ''),
        description=data.get('description', ''),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else None,
    )
    db.session.add(ach)
    db.session.commit()
    return jsonify(ach.to_dict()), 201


@resume_bp.route('/api/resume/achievements/<int:id>', methods=['DELETE'])
@login_required
def delete_achievement(id):
    ach = Achievement.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(ach)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@resume_bp.route('/api/resume/generate', methods=['POST'])
@login_required
def generate_resume():
    data = request.json or {}
    profile = ResumeProfile.query.filter_by(user_id=current_user.id).first()
    certs = Certification.query.filter_by(user_id=current_user.id).all()
    achievements = Achievement.query.filter_by(user_id=current_user.id).all()
    projects = Project.query.filter_by(user_id=current_user.id, status='Completed').all()

    resume_data = {
        'user': current_user.to_dict(),
        'profile': profile.to_dict() if profile else {},
        'certifications': [c.to_dict() for c in certs],
        'achievements': [a.to_dict() for a in achievements],
        'projects': [p.to_dict() for p in projects],
    }

    # Try AI enhancement
    enhanced = False
    try:
        from services.ai_service import enhance_resume
        enhanced_content = enhance_resume(resume_data)
        if enhanced_content:
            resume_data['ai_summary'] = enhanced_content.get('summary', '')
            resume_data['ai_project_descriptions'] = enhanced_content.get('project_descriptions', [])
            enhanced = True
    except Exception:
        pass

    resume_data['enhanced'] = enhanced
    return jsonify(resume_data)