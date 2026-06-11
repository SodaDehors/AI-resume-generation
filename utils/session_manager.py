"""Session management helpers for resume data."""

from flask import session


RESUME_FIELDS = [
    'name', 'title', 'phone', 'email', 'city', 'years_experience',
    'photo_data',  # base64 encoded image (optional)
    'education',   # list of dicts
    'experience',  # list of dicts
    'skills',      # list of dicts: {name, level}
    'certifications',  # list of dicts: {name, issuer, date}
    'languages',   # list of dicts: {name, level}
    'projects',    # list of dicts
    'self_evaluation',  # string
    'career_goal',  # string
]


def init_session():
    """Initialize session with empty resume data structure."""
    session['resume_data'] = {
        'name': '',
        'title': '',
        'phone': '',
        'email': '',
        'city': '',
        'years_experience': '',
        'photo_data': '',
        'education': [],
        'experience': [],
        'skills': [],
        'certifications': [],
        'languages': [],
        'projects': [],
        'self_evaluation': '',
        'career_goal': '',
    }
    session['current_step'] = 1
    session['generated_resume'] = None
    session['selected_template'] = 'modern'
    session['generation_status'] = 'idle'  # idle | generating | done | error
    session['ai_provider'] = 'deepseek'
    session['api_key'] = ''
    # Session ID for progress tracking
    import uuid
    session['_id'] = str(uuid.uuid4())


def get_resume_data() -> dict:
    """Get resume data from session, initializing if needed."""
    if 'resume_data' not in session:
        init_session()
    return session['resume_data']


def update_resume_field(key: str, value) -> None:
    """Update a single field in resume data."""
    data = get_resume_data()
    if key in data:
        data[key] = value
        session['resume_data'] = data


def update_resume_data(data: dict) -> None:
    """Update multiple resume data fields at once."""
    current = get_resume_data()
    current.update(data)
    session['resume_data'] = current


def get_current_step() -> int:
    """Get current wizard step."""
    return session.get('current_step', 1)


def set_current_step(step: int) -> None:
    """Set current wizard step."""
    session['current_step'] = step


def get_generated_resume() -> dict | None:
    """Get generated resume content."""
    return session.get('generated_resume')


def set_generated_resume(resume: dict) -> None:
    """Set generated resume content."""
    session['generated_resume'] = resume
    session['generation_status'] = 'done'


def set_generation_status(status: str) -> None:
    """Set generation status."""
    session['generation_status'] = status


def get_generation_status() -> str:
    """Get generation status."""
    return session.get('generation_status', 'idle')


def get_selected_template() -> str:
    """Get selected resume template name."""
    return session.get('selected_template', 'modern')


def set_selected_template(template: str) -> None:
    """Set selected resume template name."""
    session['selected_template'] = template


def get_ai_config() -> dict:
    """Get AI provider and API key from session."""
    return {
        'provider': session.get('ai_provider', 'claude'),
        'api_key': session.get('api_key', ''),
    }
