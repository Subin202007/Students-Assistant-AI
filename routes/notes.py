import os
from flask import Blueprint, request, jsonify, render_template, current_app, send_from_directory
from flask_login import login_required, current_user
from extensions import db
from models.notes import Note
from werkzeug.utils import secure_filename
from datetime import datetime

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/notes')
@login_required
def notes_page():
    return render_template('notes.html')


@notes_bp.route('/api/notes', methods=['GET'])
@login_required
def get_notes():
    subject_id = request.args.get('subject_id')
    unit = request.args.get('unit')
    search = request.args.get('search')

    query = Note.query.filter_by(user_id=current_user.id)
    if subject_id:
        query = query.filter_by(subject_id=int(subject_id))
    if unit:
        query = query.filter_by(unit=int(unit))
    if search:
        query = query.filter(Note.title.ilike(f'%{search}%') | Note.content.ilike(f'%{search}%') | Note.tags.ilike(f'%{search}%'))

    notes = query.order_by(Note.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notes])


@notes_bp.route('/api/notes', methods=['POST'])
@login_required
def create_note():
    file_path = None
    if request.files.get('file'):
        file = request.files['file']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext in current_app.config['ALLOWED_EXTENSIONS']:
                filename = secure_filename(f"note_{datetime.now().timestamp()}_{file.filename}")
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'notes', filename)
                file.save(path)
                file_path = f"notes/{filename}"

    note = Note(
        user_id=current_user.id,
        subject_id=request.form.get('subject_id') or None,
        title=request.form.get('title', ''),
        unit=int(request.form.get('unit', 0)) if request.form.get('unit') else None,
        description=request.form.get('description', ''),
        content=request.form.get('content', ''),
        file_path=file_path,
        tags=request.form.get('tags', ''),
    )
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


@notes_bp.route('/api/notes/<int:id>', methods=['PUT'])
@login_required
def update_note(id):
    note = Note.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.form if request.form else request.json
    note.title = data.get('title', note.title)
    note.description = data.get('description', note.description)
    note.content = data.get('content', note.content)
    note.tags = data.get('tags', note.tags)
    if data.get('subject_id'):
        note.subject_id = int(data['subject_id'])
    if data.get('unit'):
        note.unit = int(data['unit'])

    if request.files.get('file'):
        file = request.files['file']
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext in current_app.config['ALLOWED_EXTENSIONS']:
                filename = secure_filename(f"note_{datetime.now().timestamp()}_{file.filename}")
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'notes', filename)
                file.save(path)
                note.file_path = f"notes/{filename}"

    db.session.commit()
    return jsonify(note.to_dict())


@notes_bp.route('/api/notes/<int:id>', methods=['DELETE'])
@login_required
def delete_note(id):
    note = Note.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if note.file_path:
        try:
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], note.file_path)
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    db.session.delete(note)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@notes_bp.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)