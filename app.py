"""AI Resume Generator — Flask Application.

A web-based AI resume generation system for the ML course project.
Supports multi-step form input, AI-powered content generation,
multiple resume templates, and PDF output.
"""

import os
import logging

from flask import (Flask, render_template, request, session,
                   jsonify, redirect, url_for, make_response)

from config import DevelopmentConfig
from utils.session_manager import (
    get_resume_data, update_resume_data, update_resume_field,
    get_current_step, set_current_step,
    get_generated_resume, set_generated_resume,
    get_generation_status, set_generation_status,
    get_selected_template, set_selected_template,
    get_ai_config, init_session,
)

# In-memory progress tracking (keyed by session ID)
import threading
_gen_progress = {}
_gen_lock = threading.Lock()
from ai_service import create_llm_client
from resume.generator import ResumeGenerator
from pdf_generator.engine import generate_pdf, is_pdf_available

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """Application factory."""
    app = Flask(__name__)

    if config is None:
        app.config.from_object(DevelopmentConfig)
    else:
        app.config.from_object(config)

    # Ensure session directory exists
    session_dir = app.config.get('SESSION_FILE_DIR',
                                 os.path.join(os.path.dirname(__file__), 'flask_session'))
    os.makedirs(session_dir, exist_ok=True)

    # Register routes
    register_routes(app)
    register_error_handlers(app)

    logger.info('AI Resume Generator app created.')
    return app


def register_routes(app):
    """Register all application routes."""

    # ================================================================
    # Page routes
    # ================================================================

    @app.route('/')
    def index():
        """Landing / home page."""
        init_session()
        return render_template('index.html')

    @app.route('/form')
    def form_page():
        """Multi-step resume form."""
        if 'resume_data' not in session:
            init_session()
        return render_template('form.html',
                              current_step=get_current_step(),
                              resume_data=get_resume_data())

    @app.route('/preview')
    def preview():
        """Resume preview page (default template)."""
        template = get_selected_template()
        return redirect(url_for('preview_template', template=template))

    @app.route('/preview/<template>')
    def preview_template(template):
        """Resume preview with specific template."""
        resume = get_generated_resume()
        if not resume:
            return redirect(url_for('form_page'))

        set_selected_template(template)

        # Determine which resume template HTML to render
        template_map = {
            'classic': 'resume/classic.html',
            'modern': 'resume/modern.html',
            'compact': 'resume/compact.html',
        }
        resume_template = template_map.get(template, 'resume/modern.html')

        return render_template('preview.html',
                              resume=resume,
                              template=template,
                              resume_template=resume_template)

    @app.route('/download/<template>/pdf')
    def download_pdf(template):
        """Generate and download PDF for a specific template."""
        resume = get_generated_resume()
        if not resume:
            return redirect(url_for('form_page'))

        template_map = {
            'classic': 'resume/classic.html',
            'modern': 'resume/modern.html',
            'compact': 'resume/compact.html',
        }
        resume_template = template_map.get(template, 'resume/modern.html')

        # Render the resume HTML (without the preview UI chrome)
        html = render_template(resume_template, resume=resume)

        # CSS for PDF
        css_paths = []
        base_css = os.path.join(app.static_folder, 'css', 'base.css')
        template_css = os.path.join(app.static_folder, 'css',
                                    'templates', f'{template}.css')

        if os.path.exists(base_css):
            css_paths.append(base_css)
        if os.path.exists(template_css):
            css_paths.append(template_css)

        pdf_bytes = generate_pdf(html, css_paths)

        if pdf_bytes:
            filename = f"resume_{resume.get('name', 'output')}_{template}.pdf"
            response = make_response(pdf_bytes)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = (
                f'attachment; filename="{filename}"'
            )
            return response
        else:
            # PDF generation failed — show error with print fallback
            return render_template('error.html',
                                   message='PDF生成失败，请使用浏览器打印功能（Ctrl+P）保存为PDF。')

    # ================================================================
    # API routes
    # ================================================================

    @app.route('/api/save-step', methods=['POST'])
    def api_save_step():
        """Save form step data to session."""
        data = request.get_json(silent=True) or {}
        step = data.get('step', 1)
        fields = data.get('fields', {})

        # Update session
        update_resume_data(fields)
        set_current_step(step)

        return jsonify({'success': True, 'step': step})

    @app.route('/api/generate', methods=['POST'])
    def api_generate():
        """Trigger AI resume generation for all sections."""
        resume_data = get_resume_data()
        ai_config = get_ai_config()

        # Validate required fields
        if not resume_data.get('name') or not resume_data.get('title'):
            return jsonify({
                'success': False,
                'error': '请至少填写姓名和求职意向'
            }), 400

        set_generation_status('generating')
        sid = session.get('_id')
        if not sid:
            import uuid
            sid = str(uuid.uuid4())
            session['_id'] = sid

        def update_progress(current, total, message):
            with _gen_lock:
                _gen_progress[sid] = {
                    'current': current,
                    'total': total,
                    'message': message,
                    'percent': int(current / max(total, 1) * 100),
                }

        try:
            # Create LLM client
            client = create_llm_client(
                provider=ai_config.get('provider', 'claude'),
                api_key=ai_config.get('api_key', ''),
            )

            # Generate resume with progress
            generator = ResumeGenerator(client, progress_callback=update_progress)
            resume = generator.generate_all(resume_data)

            # Store generated resume
            set_generated_resume(resume)
            update_progress(1, 1, '✅ 简历生成完成！')

            return jsonify({
                'success': True,
                'template': get_selected_template(),
                'redirect': url_for('preview_template',
                                    template=get_selected_template()),
            })

        except Exception as e:
            logger.exception('Resume generation failed')
            set_generation_status('error')
            return jsonify({
                'success': False,
                'error': f'生成失败：{str(e)}'
            }), 500

    @app.route('/api/generate-section/<section>', methods=['POST'])
    def api_generate_section(section):
        """Generate a single resume section (for incremental/retry use)."""
        ai_config = get_ai_config()
        data = request.get_json(silent=True) or {}

        try:
            client = create_llm_client(
                provider=ai_config.get('provider', 'claude'),
                api_key=ai_config.get('api_key', ''),
            )
            generator = ResumeGenerator(client)

            section_handlers = {
                'summary': lambda: generator.generate_summary(
                    get_resume_data()),
                'experience': lambda: generator.generate_experience(data),
                'skills': lambda: generator.generate_skills(
                    get_resume_data()),
                'project': lambda: generator.generate_project(data),
                'self_eval': lambda: generator.generate_self_eval(
                    get_resume_data()),
            }

            handler = section_handlers.get(section)
            if not handler:
                return jsonify({
                    'success': False,
                    'error': f'未知的简历栏目: {section}'
                }), 400

            result = handler()
            return jsonify({'success': True, 'data': result})

        except Exception as e:
            logger.exception(f'Section generation failed: {section}')
            return jsonify({
                'success': False,
                'error': f'生成失败：{str(e)}'
            }), 500

    @app.route('/api/validate-key', methods=['POST'])
    def api_validate_key():
        """Test whether the provided API key is valid."""
        data = request.get_json(silent=True) or {}
        provider = data.get('provider', 'claude')
        api_key = data.get('api_key', '')

        if not api_key:
            return jsonify({'valid': False, 'message': 'API Key 不能为空'})

        try:
            client = create_llm_client(provider=provider, api_key=api_key)
            if client.is_available():
                # Quick test call
                test_result = client.generate(
                    system_prompt='你是一个简历助手。',
                    user_prompt='请回复"OK"。',
                    temperature=0.0,
                    max_tokens=10,
                )
                if test_result:
                    # Store in session
                    session['ai_provider'] = provider
                    session['api_key'] = api_key
                    return jsonify({'valid': True, 'message': 'API Key 验证成功'})
            return jsonify({'valid': False, 'message': 'API Key 验证失败'})
        except Exception as e:
            return jsonify({'valid': False, 'message': f'验证出错：{str(e)}'})

    @app.route('/api/status')
    def api_status():
        """Get current generation status and progress (for polling)."""
        sid = session.get('_id', '')
        progress = {'current': 0, 'total': 1, 'message': '', 'percent': 0}
        if sid:
            with _gen_lock:
                progress = _gen_progress.get(sid, progress)
        return jsonify({
            'status': get_generation_status(),
            'has_resume': get_generated_resume() is not None,
            'progress': progress,
        })

    @app.route('/api/render-resume/<template>')
    def api_render_resume(template):
        """Render just the resume HTML for AJAX template switching."""
        resume = get_generated_resume()
        if not resume:
            return jsonify({'success': False, 'error': '没有简历数据'}), 404

        template_map = {
            'classic': 'resume/classic.html',
            'modern': 'resume/modern.html',
            'compact': 'resume/compact.html',
        }
        resume_template = template_map.get(template, 'resume/modern.html')

        html = render_template(resume_template, resume=resume)
        return html

    @app.route('/api/set-provider', methods=['POST'])
    def api_set_provider():
        """Save AI provider configuration to session."""
        data = request.get_json(silent=True) or {}
        session['ai_provider'] = data.get('provider', 'claude')
        session['api_key'] = data.get('api_key', '')
        return jsonify({'success': True})


def register_error_handlers(app):
    """Register error handlers."""

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html',
                               message='页面未找到'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html',
                               message='服务器内部错误，请重试'), 500


# ================================================================
# Main entry point
# ================================================================
if __name__ == '__main__':
    app = create_app()
    print('=' * 50)
    print('AI简历生成系统')
    print('打开浏览器访问: http://127.0.0.1:5000')
    print('=' * 50)
    app.run(debug=True, host='127.0.0.1', port=5000)
