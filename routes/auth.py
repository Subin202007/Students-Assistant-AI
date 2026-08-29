from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/landing')
def landing():
    return render_template('index.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        data = request.form if request.content_type != 'application/json' else request.json
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip().lower()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        college = data.get('college', '').strip()
        department = data.get('department', '').strip()
        register_number = data.get('register_number', '').strip()
        academic_year = data.get('academic_year', '').strip()
        semester = data.get('semester', 1)

        if not all([full_name, email, password]):
            if request.is_json:
                return jsonify({'error': 'Name, email, and password are required'}), 400
            flash('Name, email, and password are required', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'Email already registered'}), 400
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password),
            college=college,
            department=department,
            register_number=register_number,
            academic_year=academic_year,
            semester=int(semester) if semester else 1,
        )
        db.session.add(user)
        db.session.commit()

        if request.is_json:
            return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        data = request.form if request.content_type != 'application/json' else request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.dashboard'))

        if request.is_json:
            return jsonify({'error': 'Invalid email or password'}), 401
        flash('Invalid email or password', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.landing'))