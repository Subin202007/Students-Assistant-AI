from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from extensions import db
from models.ai_models import ChatSession, ChatMessage, StudyMaterial, CalendarEvent
from services.ai_service import chat_with_ai, generate_study_material, generate_important_questions, summarize_notes, generate_study_plan
from datetime import datetime

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/ai-assistant')
@login_required
def ai_assistant_page():
    return render_template('ai-assistant.html')


@ai_bp.route('/study-material')
@login_required
def study_material_page():
    return render_template('study-material.html')


@ai_bp.route('/api/ai/chat', methods=['POST'])
@login_required
def ai_chat():
    data = request.json
    message = data.get('message', '').strip()
    session_id = data.get('session_id')

    if not message:
        return jsonify({'error': 'Message is required'}), 400

    # Get or create session
    if session_id:
        session = ChatSession.query.filter_by(id=session_id, user_id=current_user.id).first()
    else:
        session = None

    if not session:
        session = ChatSession(user_id=current_user.id, title=message[:50])
        db.session.add(session)
        db.session.commit()

    # Save user message
    user_msg = ChatMessage(session_id=session.id, role='user', content=message)
    db.session.add(user_msg)
    db.session.commit()

    # Get chat history
    history = ChatMessage.query.filter_by(session_id=session.id).order_by(ChatMessage.created_at).all()
    messages = [{'role': m.role, 'content': m.content} for m in history]

    # Call AI
    try:
        response = chat_with_ai(messages)
    except Exception as e:
        response = f"I'm having trouble connecting to the AI service right now. Please check your API configuration. Error: {str(e)}"

    # Save AI response
    ai_msg = ChatMessage(session_id=session.id, role='assistant', content=response)
    db.session.add(ai_msg)
    db.session.commit()

    return jsonify({
        'session_id': session.id,
        'response': response,
        'session_title': session.title,
    })


@ai_bp.route('/api/ai/sessions', methods=['GET'])
@login_required
def get_sessions():
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sessions])


@ai_bp.route('/api/ai/sessions/<int:id>', methods=['GET'])
@login_required
def get_session_messages(id):
    session = ChatSession.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    messages = ChatMessage.query.filter_by(session_id=id).order_by(ChatMessage.created_at).all()
    return jsonify({
        'session': session.to_dict(),
        'messages': [m.to_dict() for m in messages],
    })


@ai_bp.route('/api/ai/sessions/<int:id>', methods=['DELETE'])
@login_required
def delete_session(id):
    session = ChatSession.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(session)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@ai_bp.route('/api/ai/study-material', methods=['POST'])
@login_required
def ai_study_material():
    data = request.json
    subject = data.get('subject', '')
    unit = data.get('unit', '')
    topic = data.get('topic', '')
    difficulty = data.get('difficulty', 'Medium')
    exam_type = data.get('exam_type', '')

    try:
        content = generate_study_material(subject, unit, topic, difficulty, exam_type)
    except Exception as e:
        content = f"Error generating study material: {str(e)}"

    # Save
    material = StudyMaterial(
        user_id=current_user.id,
        subject=subject,
        unit=unit,
        topic=topic,
        difficulty=difficulty,
        content=content,
    )
    db.session.add(material)
    db.session.commit()

    return jsonify({'content': content, 'id': material.id})


@ai_bp.route('/api/ai/important-questions', methods=['POST'])
@login_required
def ai_important_questions():
    data = request.json
    subject = data.get('subject', '')
    semester = data.get('semester', '')
    units = data.get('units', '')
    notes_content = data.get('notes_content', '')

    try:
        content = generate_important_questions(subject, semester, units, notes_content)
    except Exception as e:
        content = f"Error generating questions: {str(e)}"

    return jsonify({'content': content})


@ai_bp.route('/api/ai/summarize', methods=['POST'])
@login_required
def ai_summarize():
    data = request.json
    notes = data.get('notes', '')
    mode = data.get('mode', 'short')

    try:
        content = summarize_notes(notes, mode)
    except Exception as e:
        content = f"Error summarizing: {str(e)}"

    return jsonify({'content': content})


@ai_bp.route('/api/ai/study-plan', methods=['POST'])
@login_required
def ai_study_plan():
    data = request.json
    try:
        content = generate_study_plan(data)
    except Exception as e:
        content = f"Error generating plan: {str(e)}"

    return jsonify({'content': content})


@ai_bp.route('/api/study-materials', methods=['GET'])
@login_required
def get_study_materials():
    materials = StudyMaterial.query.filter_by(user_id=current_user.id).order_by(StudyMaterial.created_at.desc()).all()
    return jsonify([m.to_dict() for m in materials])


@ai_bp.route('/api/calendar/events', methods=['GET'])
@login_required
def get_events():
    events = CalendarEvent.query.filter_by(user_id=current_user.id).all()
    return jsonify([e.to_dict() for e in events])


@ai_bp.route('/api/calendar/events', methods=['POST'])
@login_required
def create_event():
    data = request.json
    event = CalendarEvent(
        user_id=current_user.id,
        title=data.get('title', ''),
        event_type=data.get('event_type', ''),
        date=datetime.strptime(data['date'], '%Y-%m-%d').date() if data.get('date') else datetime.now().date(),
        time=data.get('time', ''),
        description=data.get('description', ''),
        color=data.get('color', '#4f46e5'),
    )
    db.session.add(event)
    db.session.commit()
    return jsonify(event.to_dict()), 201


@ai_bp.route('/api/calendar/events/<int:id>', methods=['PUT'])
@login_required
def update_event(id):
    event = CalendarEvent.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    data = request.json
    for field in ['title', 'event_type', 'time', 'description', 'color']:
        if field in data:
            setattr(event, field, data[field])
    if 'completed' in data:
        event.completed = bool(data['completed'])
    if data.get('date'):
        event.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(event.to_dict())


@ai_bp.route('/api/calendar/events/<int:id>', methods=['DELETE'])
@login_required
def delete_event(id):
    event = CalendarEvent.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@ai_bp.route('/api/search', methods=['GET'])
@login_required
def global_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({'results': []})

    from models.notes import Note
    from models.assignments import Assignment
    from models.projects import Project

    results = []

    notes = Note.query.filter_by(user_id=current_user.id).filter(
        (Note.title.ilike(f'%{q}%')) | (Note.content.ilike(f'%{q}%')) | (Note.tags.ilike(f'%{q}%'))
    ).limit(10).all()
    for n in notes:
        results.append({'type': 'note', 'title': n.title, 'id': n.id, 'description': n.description or ''})

    assignments = Assignment.query.filter_by(user_id=current_user.id).filter(
        (Assignment.title.ilike(f'%{q}%')) | (Assignment.description.ilike(f'%{q}%'))
    ).limit(10).all()
    for a in assignments:
        results.append({'type': 'assignment', 'title': a.title, 'id': a.id, 'description': a.description or ''})

    projects = Project.query.filter_by(user_id=current_user.id).filter(
        (Project.title.ilike(f'%{q}%')) | (Project.description.ilike(f'%{q}%')) | (Project.technologies.ilike(f'%{q}%'))
    ).limit(10).all()
    for p in projects:
        results.append({'type': 'project', 'title': p.title, 'id': p.id, 'description': p.description or ''})

    return jsonify({'results': results})