/* ============================================================
   Preview Page - AJAX template switching, download, print
   ============================================================ */

let currentTemplate = document.querySelector('.tpl-btn.active')?.id?.replace('tpl-btn-', '') || 'modern';

document.addEventListener('DOMContentLoaded', () => {
    highlightActiveTemplate();
});

/**
 * Switch resume template via AJAX — no page reload.
 */
async function switchTemplate(template) {
    if (template === currentTemplate) return;

    // Update button states
    document.querySelectorAll('.tpl-btn').forEach(b => b.classList.remove('active'));
    const btn = document.getElementById(`tpl-btn-${template}`);
    if (btn) btn.classList.add('active');
    currentTemplate = template;

    // Show loading state on resume page
    const page = document.getElementById('resume-page');
    page.style.opacity = '0.4';
    page.style.transition = 'opacity 0.15s';

    try {
        const resp = await fetch(`/api/render-resume/${template}`);
        if (!resp.ok) throw new Error('Render failed');
        const html = await resp.text();
        page.innerHTML = html;
        page.style.opacity = '1';

        // Swap CSS
        const cssLink = document.getElementById('template-css');
        if (cssLink) {
            cssLink.href = `/static/css/templates/${template}.css`;
        }

        // Update download link
        const downBtn = document.getElementById('btn-download');
        if (downBtn) {
            downBtn.href = `/download/${template}/pdf`;
        }

        // Update URL without reload
        if (history.pushState) {
            history.pushState(null, '', `/preview/${template}`);
        }
    } catch (err) {
        page.style.opacity = '1';
        console.error('Template switch failed:', err);
    }
}

function highlightActiveTemplate() {
    const path = window.location.pathname;
    document.querySelectorAll('.tpl-btn').forEach(btn => {
        const id = btn.id.replace('tpl-btn-', '');
        if (path.includes(id)) {
            btn.classList.add('active');
            currentTemplate = id;
        } else {
            btn.classList.remove('active');
        }
    });
}
