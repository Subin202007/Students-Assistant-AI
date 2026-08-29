import os
import requests
from flask import current_app

def get_ai_config():
    """Get AI configuration from app config or environment."""
    try:
        api_key = current_app.config.get('AI_API_KEY', '')
        api_url = current_app.config.get('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
        model = current_app.config.get('AI_MODEL', 'gpt-3.5-turbo')
    except RuntimeError:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('AI_API_KEY', '')
        api_url = os.getenv('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
        model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
    return api_key, api_url, model


def call_ai_api(messages, system_prompt="You are EduAI, a helpful academic assistant for students."):
    """Generic AI API caller."""
    api_key, api_url, model = get_ai_config()

    if not api_key or api_key == 'your_api_key_here':
        return _fallback_response(messages, system_prompt)

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        'model': model,
        'messages': [{'role': 'system', 'content': system_prompt}] + messages,
        'temperature': 0.7,
        'max_tokens': 1500,
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"AI service error: {str(e)}"


def _fallback_response(messages, system_prompt):
    """Fallback when no API key is configured."""
    last_msg = messages[-1]['content'] if messages else ''
    return (
        f"📚 **EduAI (Demo Mode)**\n\n"
        f"I received your message: \"{last_msg[:100]}\"\n\n"
        f"To enable full AI features, please configure your `AI_API_KEY` in the `.env` file.\n\n"
        f"I can help with:\n"
        f"- Academic concepts\n"
        f"- Programming questions\n"
        f"- Study planning\n"
        f"- Exam preparation\n\n"
        f"*This is a demo response. Configure an API key for real AI assistance.*"
    )


def chat_with_ai(messages):
    """Chat with AI using conversation history."""
    system = (
        "You are EduAI, an intelligent academic assistant for students. "
        "Help with academic questions, programming doubts, mathematics explanations, "
        "study planning, assignment guidance, exam preparation, concept explanations, "
        "revision planning, and notes summarization. "
        "Be clear, educational, and encouraging. "
        "If you are uncertain about something, acknowledge it honestly. "
        "Use markdown formatting for clarity."
    )
    return call_ai_api(messages, system)


def generate_study_material(subject, unit, topic, difficulty, exam_type):
    """Generate study material for a topic."""
    prompt = (
        f"Generate comprehensive study material for:\n"
        f"Subject: {subject}\n"
        f"Unit: {unit}\n"
        f"Topic: {topic}\n"
        f"Difficulty: {difficulty}\n"
        f"Exam Type: {exam_type}\n\n"
        f"Please provide:\n"
        f"1. Simple explanation\n"
        f"2. Detailed notes\n"
        f"3. Key points\n"
        f"4. Important definitions\n"
        f"5. Important formulas (if applicable)\n"
        f"6. Examples\n"
        f"7. Revision summary\n"
        f"8. Possible exam questions\n"
        f"9. Flashcards (term: definition)\n"
        f"10. Quiz questions (3-5)\n\n"
        f"Use markdown formatting."
    )
    return call_ai_api([{'role': 'user', 'content': prompt}], "You are an expert academic content generator.")


def generate_important_questions(subject, semester, units, notes_content):
    """Generate important questions based on supplied material."""
    prompt = (
        f"Based on the following information, generate likely important exam questions.\n\n"
        f"Subject: {subject}\n"
        f"Semester: {semester}\n"
        f"Units covered: {units}\n\n"
    )
    if notes_content:
        prompt += f"Study material / notes provided:\n{notes_content[:3000]}\n\n"

    prompt += (
        f"Please generate:\n"
        f"1. HIGH PRIORITY questions (likely to appear)\n"
        f"2. MEDIUM PRIORITY questions\n"
        f"3. Unit-wise important topics\n"
        f"4. Frequently occurring concepts\n"
        f"5. Possible long-answer topics\n"
        f"6. Short-answer revision questions\n\n"
        f"IMPORTANT: Do NOT claim these are the exact exam questions. "
        f"Use wording like 'Likely important based on supplied materials and patterns.'\n"
        f"Use markdown formatting."
    )
    return call_ai_api([{'role': 'user', 'content': prompt}], "You are an academic exam preparation expert.")


def summarize_notes(notes, mode='short'):
    """Summarize user-provided notes."""
    mode_instruction = {
        'short': 'Provide a brief summary (2-3 paragraphs).',
        'detailed': 'Provide a detailed summary covering all key points.',
        'points': 'Extract the most important points as a bullet list.',
        'questions': 'Generate revision questions based on these notes.',
        'flashcards': 'Generate flashcards (term: definition) from these notes.',
    }.get(mode, 'Provide a summary.')

    prompt = (
        f"Summarize the following notes. {mode_instruction}\n\n"
        f"Notes:\n{notes[:4000]}\n\n"
        f"Only summarize the content provided. Do not add external information.\n"
        f"Use markdown formatting."
    )
    return call_ai_api([{'role': 'user', 'content': prompt}], "You are an expert note summarizer.")


def generate_study_plan(data):
    """Generate a personalized study plan."""
    prompt = (
        f"Generate a practical study schedule based on:\n"
        f"Subjects: {data.get('subjects', '')}\n"
        f"Exam dates: {data.get('exam_dates', '')}\n"
        f"Available study hours per day: {data.get('hours_per_day', '4')}\n"
        f"Weak subjects: {data.get('weak_subjects', '')}\n"
        f"Strong subjects: {data.get('strong_subjects', '')}\n"
        f"Target grade: {data.get('target_grade', 'Good')}\n\n"
        f"Create a day-by-day study plan with time slots. "
        f"Allocate more time to weak subjects. Include revision slots and breaks.\n"
        f"Use markdown formatting."
    )
    return call_ai_api([{'role': 'user', 'content': prompt}], "You are an expert academic study planner.")


def enhance_resume(resume_data):
    """Enhance resume content using AI."""
    user = resume_data.get('user', {})
    profile = resume_data.get('profile', {})
    projects = resume_data.get('projects', [])

    prompt = (
        f"Generate professional resume content based on this student's information:\n\n"
        f"Name: {user.get('full_name', '')}\n"
        f"Department: {user.get('department', '')}\n"
        f"College: {user.get('college', '')}\n"
        f"CGPA/Semester: {user.get('semester', '')}\n"
        f"Skills: {profile.get('skills', '')}\n"
        f"Projects: {', '.join([p.get('title', '') for p in projects])}\n\n"
        f"Please generate:\n"
        f"1. A professional summary (2-3 sentences)\n"
        f"2. Brief professional descriptions for each project (based ONLY on the titles and info given)\n\n"
        f"Do NOT invent qualifications, achievements, or experience not provided.\n"
        f"Return as JSON with keys: summary, project_descriptions (array of strings)."
    )
    try:
        response = call_ai_api([{'role': 'user', 'content': prompt}], "You are a professional resume writer.")
        import json
        # Try to parse JSON from response
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
        return {'summary': response, 'project_descriptions': []}
    except Exception:
        return None