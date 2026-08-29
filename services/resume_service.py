def generate_resume_content(user, profile, projects, certifications, achievements):
    """Build resume data structure."""
    return {
        'personal': {
            'name': user.full_name,
            'email': user.email,
            'phone': user.phone,
            'location': profile.get('location', '') if profile else '',
            'linkedin': profile.get('linkedin', '') if profile else '',
            'github': profile.get('github', '') if profile else '',
            'portfolio': profile.get('portfolio', '') if profile else '',
        },
        'education': {
            'college': user.college,
            'department': user.department,
            'semester': user.semester,
        },
        'skills': (profile.get('skills', '') if profile else '').split(','),
        'projects': projects,
        'certifications': certifications,
        'achievements': achievements,
        'summary': profile.get('summary', '') if profile else '',
    }