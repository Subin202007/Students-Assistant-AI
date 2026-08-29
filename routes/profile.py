import os
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from extensions import db
from models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/profile')
@login_required
def profile_page():
    return render_template('profile.html')


@profile_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify(current_user.to_dict())


@profile_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.form if request.form else request.json
    for field in ['full_name', 'phone', 'college', 'department', 'register_number', 'academic_year']:
        if field in data:
            setattr(current_user, field, data[field])
    if data.get('semester'):
        current_user.semester = int(data['semester'])

    if request.files.get('photo'):
        file = request.files['photo']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext in ['png', 'jpg', 'jpeg']:
                filename = secure_filename(f"profile_{current_user.id}_{datetime.now().timestamp()}.{ext}")
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'profile', filename)
                file.save(path)
                current_user.profile_photo = f"profile/{filename}"

    db.session.commit()
    return jsonify(current_user.to_dict())


@profile_bp.route('/api/profile/password', methods=['POST'])
@login_required
def change_password():
    data = request.json
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')

    if not check_password_hash(current_user.password_hash, current_password):
        return jsonify({'error': 'Current password is incorrect'}), 400

    if len(new_password) < 6:
        return jsonify({'error': 'New password must be at least 6 characters'}), 400

    current_user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    return jsonify({'message': 'Password changed successfully'})