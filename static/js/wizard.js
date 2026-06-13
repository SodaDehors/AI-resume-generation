/* ============================================================
   Multi-Step Form Wizard
   Handles navigation, validation, dynamic fields, and submission
   ============================================================ */

const TOTAL_STEPS = 6;
let currentStep = 1;
let _hasUnsavedChanges = false;

// ============================================================
// Initialization
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    initSkillTagInput();
    initTemplateSelector();
    initBackToTop();
    initBeforeUnload();
    updateProgressBar();
    updateNavButtons();
});

// ============================================================
// Step Navigation
// ============================================================
function nextStep() {
    if (currentStep >= TOTAL_STEPS) return;

    if (!validateStep(currentStep)) return;

    // Save current step data
    saveCurrentStep();

    // Advance
    currentStep++;
    showStep(currentStep);
    updateProgressBar();
    updateNavButtons();
}

function prevStep() {
    if (currentStep <= 1) return;

    saveCurrentStep();
    currentStep--;
    showStep(currentStep);
    updateProgressBar();
    updateNavButtons();
}

function showStep(step) {
    document.querySelectorAll('.step-panel').forEach(p => p.classList.remove('active'));
    const panel = document.querySelector(`.step-panel[data-step="${step}"]`);
    if (panel) panel.classList.add('active');

    document.getElementById('step-indicator').textContent = `${step} / ${TOTAL_STEPS}`;
}

function updateProgressBar() {
    document.querySelectorAll('.progress-step').forEach(el => {
        const stepNum = parseInt(el.dataset.step);
        el.classList.remove('active', 'completed');
        if (stepNum === currentStep) el.classList.add('active');
        if (stepNum < currentStep) el.classList.add('completed');
    });

    document.querySelectorAll('.progress-line').forEach(el => {
        const prevStepEl = el.previousElementSibling;
        if (prevStepEl && prevStepEl.classList.contains('completed')) {
            el.classList.add('completed');
        } else {
            el.classList.remove('completed');
        }
    });
}

function updateNavButtons() {
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnGenerate = document.getElementById('btn-generate');

    btnPrev.disabled = currentStep <= 1;

    if (currentStep >= TOTAL_STEPS) {
        btnNext.style.display = 'none';
        btnGenerate.style.display = 'inline-flex';
    } else {
        btnNext.style.display = 'inline-flex';
        btnGenerate.style.display = 'none';
    }
}

// ============================================================
// Validation
// ============================================================
function validateStep(step) {
    clearErrors();

    switch (step) {
        case 1: return validateStep1();
        case 2: return true; // Education is optional
        case 3: return true; // Experience is optional
        case 4: return true; // Skills are optional
        case 5: return true; // Projects are optional
        case 6: return validateStep6();
        default: return true;
    }
}

function validateStep1() {
    let valid = true;
    const name = document.getElementById('name').value.trim();
    const title = document.getElementById('title').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const email = document.getElementById('email').value.trim();

    if (!name || name.length < 2) {
        showError('name', '请输入有效的姓名（至少2个字符）');
        valid = false;
    }
    if (!title) {
        showError('title', '请输入求职意向');
        valid = false;
    }
    if (!phone) {
        showError('phone', '请输入手机号');
        valid = false;
    } else if (!/^1[3-9]\d{9}$/.test(phone)) {
        showError('phone', '请输入有效的11位手机号');
        valid = false;
    }
    if (!email) {
        showError('email', '请输入邮箱地址');
        valid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        showError('email', '请输入有效的邮箱地址');
        valid = false;
    }
    return valid;
}

function validateStep6() {
    // AI provider settings validation
    const provider = document.getElementById('ai-provider').value;
    if (provider !== 'fallback') {
        const apiKey = document.getElementById('api-key').value.trim();
        if (!apiKey) {
            // API Key is optional; will use fallback
            showWarning('api-key', '未填写API Key，将使用模板模式生成');
        }
    }
    return true;
}

function showError(fieldId, message) {
    const el = document.getElementById(fieldId);
    if (el) {
        el.classList.add('error');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'form-error';
        errorDiv.textContent = message;
        el.parentNode.appendChild(errorDiv);
    }
}

function showWarning(fieldId, message) {
    const el = document.getElementById(fieldId);
    if (el) {
        const hint = el.parentNode.querySelector('.form-hint');
        if (hint) {
            hint.textContent = message;
            hint.style.color = '#f57f17';
        }
    }
}

function clearErrors() {
    document.querySelectorAll('.form-error').forEach(e => e.remove());
    document.querySelectorAll('input.error, textarea.error').forEach(e => e.classList.remove('error'));
    // Reset hints
    document.querySelectorAll('.form-hint').forEach(h => h.style.color = '');
}

// ============================================================
// Save data to session
// ============================================================
async function saveCurrentStep() {
    const fields = {};

    if (currentStep === 1) {
        fields.name = document.getElementById('name').value.trim();
        fields.title = document.getElementById('title').value.trim();
        fields.phone = document.getElementById('phone').value.trim();
        fields.email = document.getElementById('email').value.trim();
        fields.city = document.getElementById('city').value.trim();
        fields.years_experience = document.getElementById('years_experience').value;
    }

    if (currentStep === 2) {
        fields.education = collectEducation();
    }

    if (currentStep === 3) {
        fields.experience = collectExperience();
    }

    if (currentStep === 4) {
        fields.skills = collectSkills();
        fields.languages = collectLanguages();
        fields.certifications = collectCertifications();
    }

    if (currentStep === 5) {
        fields.projects = collectProjects();
    }

    if (currentStep === 6) {
        fields.self_evaluation = document.getElementById('self_evaluation').value.trim();
        fields.career_goal = document.getElementById('career_goal').value.trim();
        fields.selected_template = getSelectedTemplate();

        // Also save AI config
        const provider = document.getElementById('ai-provider').value;
        const apiKey = document.getElementById('api-key').value.trim();
        await API.setProvider(provider, apiKey);
    }

    if (Object.keys(fields).length > 0) {
        await API.saveStep(currentStep, fields);
    }
}

// ============================================================
// Generate Resume (with real progress polling + cancel)
// ============================================================
let _pollTimer = null;
let _abortController = null;

async function generateResume() {
    // Validate and save step 6
    if (!validateStep(6)) return;
    await saveCurrentStep();

    // Show loading overlay
    const overlay = document.getElementById('loading-overlay');
    const statusText = document.getElementById('loading-status');
    const progressFill = document.getElementById('progress-bar-fill');
    const cancelBtn = document.getElementById('btn-cancel-generate');

    overlay.style.display = 'flex';
    statusText.textContent = '正在连接 AI 服务...';
    progressFill.style.width = '0%';
    cancelBtn.style.display = 'inline-flex';
    _abortController = new AbortController();

    // Start polling for real progress
    _pollTimer = setInterval(async () => {
        try {
            const resp = await fetch('/api/status');
            const status = await resp.json();
            if (status.progress && status.progress.message) {
                const pct = status.progress.percent || 0;
                statusText.textContent = status.progress.message;
                progressFill.style.width = pct + '%';
            }
        } catch (e) { /* ignore poll errors */ }
    }, 500);

    try {
        const result = await API.generateResume(_abortController.signal);
        clearInterval(_pollTimer);

        if (result.success) {
            progressFill.style.width = '100%';
            statusText.textContent = '✅ 简历生成成功！正在跳转...';
            cancelBtn.style.display = 'none';
            _hasUnsavedChanges = false;
            setTimeout(() => {
                window.location.href = result.redirect || '/preview';
            }, 600);
        } else {
            overlay.style.display = 'none';
            alert('生成失败：' + (result.error || '未知错误'));
        }
    } catch (err) {
        clearInterval(_pollTimer);
        if (err.name === 'AbortError') {
            statusText.textContent = '已取消生成';
        } else {
            overlay.style.display = 'none';
            alert('网络错误，请检查服务器连接：' + err.message);
        }
    }
}

function cancelGeneration() {
    if (_abortController) {
        _abortController.abort();
        _abortController = null;
    }
    if (_pollTimer) {
        clearInterval(_pollTimer);
        _pollTimer = null;
    }
    document.getElementById('loading-overlay').style.display = 'none';
    showToast('已取消生成，可以继续修改');
}

// ============================================================
// Load Sample Data — one-click demo fill
// ============================================================
function loadSampleData() {
    if (!confirm('加载示例数据将覆盖当前已填写的内容，确认继续？')) return;

    // Step 1: Basic info
    document.getElementById('name').value = '林远航';
    document.getElementById('title').value = '全栈开发工程师';
    document.getElementById('phone').value = '13987654321';
    document.getElementById('email').value = 'linyuanhang@example.com';
    document.getElementById('city').value = '深圳';
    document.getElementById('years_experience').value = '3-5年';

    // Step 2: Education
    document.getElementById('education-list').innerHTML = '';
    addEducation({ school: '浙江大学', degree: '硕士', major: '计算机科学与技术', start_date: '2018-09', end_date: '2021-06' });
    addEducation({ school: '华中科技大学', degree: '本科', major: '软件工程', start_date: '2014-09', end_date: '2018-06' });

    // Step 3: Work Experience
    document.getElementById('experience-list').innerHTML = '';
    addExperience({
        company: '腾讯科技（深圳）有限公司', title: '高级前端开发工程师',
        start_date: '2023-03', end_date: '至今',
        raw_description: '负责腾讯云控制台前端架构设计与核心模块开发，主导了控制台2.0版本的全面重构。带领4人团队，使用React+TypeScript技术栈，将页面加载性能提升了40%，组件复用率从30%提升到70%。'
    });
    addExperience({
        company: '字节跳动', title: '前端开发工程师',
        start_date: '2021-07', end_date: '2023-02',
        raw_description: '参与抖音电商后台管理系统的前端开发，负责商品管理、订单管理、数据看板等核心模块。使用Vue3+Pinia+Element Plus开发，独立完成了数据可视化看板的从0到1搭建，支撑日均10万+订单的数据展示。'
    });

    // Step 4: Skills
    document.getElementById('skills-tags').innerHTML = '';
    ['JavaScript/TypeScript', 'React', 'Vue3', 'Node.js', 'Python', 'MySQL', 'Docker', 'Git', 'Linux'].forEach(s => addSkillTag(s));
    document.getElementById('languages-list').innerHTML = '';
    addLanguage({ name: '英语', level: '流利' });
    addLanguage({ name: '普通话', level: '母语' });
    document.getElementById('certifications-list').innerHTML = '';
    addCertification({ name: 'AWS Solutions Architect Associate', issuer: 'Amazon Web Services' });
    addCertification({ name: '软考中级 - 软件设计师', issuer: '人社部/工信部' });

    // Step 5: Projects
    document.getElementById('projects-list').innerHTML = '';
    addProject({
        name: '智慧校园综合管理平台', role: '全栈开发负责人',
        technologies: 'React, Node.js, Express, MongoDB, Redis, Docker',
        raw_description: '为某高校定制的校园管理SaaS平台，涵盖教务管理、学生事务、宿舍分配等模块。采用微服务架构，支持5000+并发用户。'
    });
    addProject({
        name: '实时数据可视化大屏', role: '前端架构 + 数据对接',
        technologies: 'Vue3, ECharts, WebSocket, TypeScript, Pinia',
        raw_description: '为企业决策层打造的实时业务数据大屏，对接多个数据源，支持动态刷新和钻取分析，获公司年度最佳技术项目奖。'
    });

    // Step 6: Self-evaluation & settings
    document.getElementById('self_evaluation').value = '热爱技术，持续关注前端领域前沿动态。工作中注重代码质量和用户体验，擅长在技术深度和业务交付之间找到平衡。具备良好的跨团队沟通能力，习惯从产品视角思考技术方案。';
    document.getElementById('career_goal').value = '期望在全栈开发领域持续深耕，成为技术专家，参与有影响力的产品研发';

    // Go back to step 1 so user can review
    currentStep = 1;
    showStep(1);
    updateProgressBar();
    updateNavButtons();

    showToast('✅ 示例数据已加载，可逐步骤查看和修改');
}

// ============================================================
// Toast notification
// ============================================================
function showToast(message) {
    let toast = document.getElementById('toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style.cssText = `
            position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
            background: #FFE01B; color: #241C15; padding: 12px 28px;
            border-radius: 9999px; font-size: 0.88rem; z-index: 9999;
            box-shadow: 0 4px 12px rgba(36,28,21,0.12);
            font-weight: 700; letter-spacing: 0.01em;
            transition: opacity 0.3s; font-family: inherit;
        `;
        document.body.appendChild(toast);
    }
    toast.textContent = message;
    toast.style.opacity = '1';
    clearTimeout(toast._timeout);
    toast._timeout = setTimeout(() => { toast.style.opacity = '0'; }, 2500);
}

// ============================================================
// Dynamic Education Entries
// ============================================================
function addEducation(data = {}) {
    const list = document.getElementById('education-list');
    const index = list.children.length;
    const div = document.createElement('div');
    div.className = 'entry-card';
    div.innerHTML = `
        <button class="entry-remove" onclick="this.parentElement.remove()"><span class="remove-icon"></span></button>
        <div class="form-row">
            <div class="form-group">
                <label>学校名称</label>
                <input type="text" class="edu-school" value="${esc(data.school || '')}" placeholder="如：清华大学">
            </div>
            <div class="form-group">
                <label>学位</label>
                <select class="edu-degree">
                    ${selectOptions(['本科', '硕士', '博士', '大专', '其他'], data.degree)}
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>专业</label>
                <input type="text" class="edu-major" value="${esc(data.major || '')}" placeholder="如：计算机科学与技术">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>开始时间</label>
                <input type="text" class="edu-start" value="${esc(data.start_date || '')}" placeholder="YYYY-MM">
            </div>
            <div class="form-group">
                <label>结束时间</label>
                <input type="text" class="edu-end" value="${esc(data.end_date || '')}" placeholder="YYYY-MM 或 至今">
            </div>
        </div>
    `;
    list.appendChild(div);
}

function collectEducation() {
    const items = [];
    document.querySelectorAll('#education-list .entry-card').forEach(card => {
        items.push({
            school: card.querySelector('.edu-school').value.trim(),
            degree: card.querySelector('.edu-degree').value,
            major: card.querySelector('.edu-major').value.trim(),
            start_date: card.querySelector('.edu-start').value.trim(),
            end_date: card.querySelector('.edu-end').value.trim(),
        });
    });
    return items;
}

// ============================================================
// Dynamic Experience Entries
// ============================================================
function addExperience(data = {}) {
    const list = document.getElementById('experience-list');
    const div = document.createElement('div');
    div.className = 'entry-card';
    div.innerHTML = `
        <button class="entry-remove" onclick="this.parentElement.remove()"><span class="remove-icon"></span></button>
        <div class="form-row">
            <div class="form-group">
                <label>公司名称</label>
                <input type="text" class="exp-company" value="${esc(data.company || '')}" placeholder="如：阿里巴巴">
            </div>
            <div class="form-group">
                <label>职位</label>
                <input type="text" class="exp-title" value="${esc(data.title || '')}" placeholder="如：高级Java开发工程师">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label>开始时间</label>
                <input type="text" class="exp-start" value="${esc(data.start_date || '')}" placeholder="YYYY-MM">
            </div>
            <div class="form-group">
                <label>结束时间</label>
                <input type="text" class="exp-end" value="${esc(data.end_date || '')}" placeholder="YYYY-MM 或 至今">
            </div>
        </div>
        <div class="form-group">
            <label>工作内容描述 <span style="color:#999;font-weight:400;">（AI将自动优化为专业要点）</span></label>
            <textarea class="exp-desc" rows="3" placeholder="简单描述您的主要职责和工作成果即可，AI会帮您优化措辞并量化成果">${esc(data.raw_description || '')}</textarea>
        </div>
    `;
    list.appendChild(div);
}

function collectExperience() {
    const items = [];
    document.querySelectorAll('#experience-list .entry-card').forEach(card => {
        items.push({
            company: card.querySelector('.exp-company').value.trim(),
            title: card.querySelector('.exp-title').value.trim(),
            start_date: card.querySelector('.exp-start').value.trim(),
            end_date: card.querySelector('.exp-end').value.trim(),
            raw_description: card.querySelector('.exp-desc').value.trim(),
        });
    });
    return items;
}

// ============================================================
// Skills Tag Input
// ============================================================
function initSkillTagInput() {
    const input = document.getElementById('skill-input');
    if (!input) return;

    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const value = this.value.trim();
            if (value) {
                addSkillTag(value);
                this.value = '';
            }
        }
    });
}

function addSkillTag(name) {
    const tagList = document.getElementById('skills-tags');
    const tag = document.createElement('span');
    tag.className = 'tag-item';
    tag.innerHTML = `${esc(name)} <span class="tag-remove" onclick="this.parentElement.remove()">×</span>`;
    tagList.appendChild(tag);
}

function collectSkills() {
    const skills = [];
    document.querySelectorAll('#skills-tags .tag-item').forEach(tag => {
        const name = tag.textContent.replace('×', '').trim();
        if (name) skills.push({ name, level: '掌握' });
    });
    return skills;
}

// ============================================================
// Languages
// ============================================================
function addLanguage(data = {}) {
    const list = document.getElementById('languages-list');
    const div = document.createElement('div');
    div.className = 'lang-row';
    div.innerHTML = `
        <input type="text" class="lang-name" value="${esc(data.name || '')}" placeholder="语言名称（如：英语）">
        <select class="lang-level">
            ${selectOptions(['母语', '流利', '良好', '基础'], data.level)}
        </select>
        <button class="btn btn-outline btn-sm" onclick="this.parentElement.remove()">删除</button>
    `;
    list.appendChild(div);
}

function collectLanguages() {
    const items = [];
    document.querySelectorAll('#languages-list .lang-row').forEach(row => {
        const name = row.querySelector('.lang-name').value.trim();
        const level = row.querySelector('.lang-level').value;
        if (name) items.push({ name, level });
    });
    return items;
}

// ============================================================
// Certifications
// ============================================================
function addCertification(data = {}) {
    const list = document.getElementById('certifications-list');
    const div = document.createElement('div');
    div.className = 'cert-row';
    div.innerHTML = `
        <input type="text" class="cert-name" value="${esc(data.name || '')}" placeholder="证书名称（如：PMP项目管理）">
        <input type="text" class="cert-issuer" value="${esc(data.issuer || '')}" placeholder="颁发机构">
        <button class="btn btn-outline btn-sm" onclick="this.parentElement.remove()">删除</button>
    `;
    list.appendChild(div);
}

function collectCertifications() {
    const items = [];
    document.querySelectorAll('#certifications-list .cert-row').forEach(row => {
        const name = row.querySelector('.cert-name').value.trim();
        const issuer = row.querySelector('.cert-issuer').value.trim();
        if (name) items.push({ name, issuer });
    });
    return items;
}

// ============================================================
// Projects
// ============================================================
function addProject(data = {}) {
    const list = document.getElementById('projects-list');
    const div = document.createElement('div');
    div.className = 'entry-card';
    div.innerHTML = `
        <button class="entry-remove" onclick="this.parentElement.remove()"><span class="remove-icon"></span></button>
        <div class="form-row">
            <div class="form-group">
                <label>项目名称</label>
                <input type="text" class="proj-name" value="${esc(data.name || '')}" placeholder="如：电商推荐系统">
            </div>
            <div class="form-group">
                <label>担任角色</label>
                <input type="text" class="proj-role" value="${esc(data.role || '')}" placeholder="如：核心开发 / 项目负责人">
            </div>
        </div>
        <div class="form-group">
            <label>使用技术</label>
            <input type="text" class="proj-tech" value="${esc(data.technologies || '')}" placeholder="如：Python, Django, MySQL, Redis">
        </div>
        <div class="form-group">
            <label>项目简介 <span style="color:#999;font-weight:400;">（AI将自动优化描述）</span></label>
            <textarea class="proj-desc" rows="2" placeholder="简要描述项目背景和你的贡献">${esc(data.raw_description || '')}</textarea>
        </div>
    `;
    list.appendChild(div);
}

function collectProjects() {
    const items = [];
    document.querySelectorAll('#projects-list .entry-card').forEach(card => {
        items.push({
            name: card.querySelector('.proj-name').value.trim(),
            role: card.querySelector('.proj-role').value.trim(),
            technologies: card.querySelector('.proj-tech').value.trim(),
            raw_description: card.querySelector('.proj-desc').value.trim(),
        });
    });
    return items;
}

// ============================================================
// Template Selector (Step 6)
// ============================================================
function initTemplateSelector() {
    document.querySelectorAll('.template-option').forEach(option => {
        option.addEventListener('click', function() {
            document.querySelectorAll('.template-option').forEach(o => o.classList.remove('selected'));
            this.classList.add('selected');
            // Persist template choice immediately
            const template = this.dataset.template;
            fetch('/api/save-step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ step: 6, fields: { selected_template: template } }),
            }).catch(() => {});
        });
    });
}

function getSelectedTemplate() {
    const selected = document.querySelector('.template-option.selected');
    return selected ? selected.dataset.template : 'modern';
}

// ============================================================
// Utilities
// ============================================================
function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function selectOptions(options, selectedValue) {
    return options.map(opt =>
        `<option value="${opt}" ${opt === selectedValue ? 'selected' : ''}>${opt}</option>`
    ).join('');
}

// ============================================================
// Back to Top Button
// ============================================================
function initBackToTop() {
    const btn = document.createElement('button');
    btn.id = 'back-to-top';
    btn.innerHTML = '↑';
    btn.title = '回到顶部';
    btn.style.cssText = `
        position: fixed; bottom: 28px; right: 28px;
        width: 44px; height: 44px; border-radius: 50%;
        background: #FFE01B; color: #241C15; border: 3px solid #241C15;
        font-size: 1.2rem; cursor: pointer; z-index: 99;
        font-family: inherit; font-weight: 800;
        box-shadow: 0 4px 12px rgba(36,28,21,0.12);
        opacity: 0; pointer-events: none;
        transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1);
    `;
    btn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
    document.body.appendChild(btn);

    window.addEventListener('scroll', () => {
        const show = window.scrollY > 400;
        btn.style.opacity = show ? '1' : '0';
        btn.style.pointerEvents = show ? 'auto' : 'none';
    });
}

// ============================================================
// BeforeUnload — warn on unsaved changes
// ============================================================
function initBeforeUnload() {
    // Mark dirty on any form input change
    document.addEventListener('input', () => { _hasUnsavedChanges = true; });
    document.addEventListener('change', () => { _hasUnsavedChanges = true; });

    window.addEventListener('beforeunload', (e) => {
        if (_hasUnsavedChanges && !document.getElementById('loading-overlay').style.display.includes('flex')) {
            e.preventDefault();
            e.returnValue = '您填写的内容尚未保存，确定要离开吗？';
            return e.returnValue;
        }
    });
}

// ============================================================
// Live field validation feedback
// ============================================================
document.addEventListener('input', (e) => {
    const el = e.target;
    if (!el.closest('#wizard-content')) return;

    // Remove error state on input
    if (el.classList.contains('error')) {
        el.classList.remove('error');
        const errorDiv = el.parentNode.querySelector('.form-error');
        if (errorDiv) errorDiv.remove();
    }

    // Add subtle valid indicator for key fields
    if (['name', 'title', 'phone', 'email'].includes(el.id) && el.value.trim()) {
        if (el.id === 'name' && el.value.trim().length >= 2) el.classList.add('valid');
        else if (el.id === 'title' && el.value.trim()) el.classList.add('valid');
        else if (el.id === 'phone' && /^1[3-9]\d{9}$/.test(el.value.trim())) el.classList.add('valid');
        else if (el.id === 'email' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value.trim())) el.classList.add('valid');
    }
});
