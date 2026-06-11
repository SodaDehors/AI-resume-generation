"""Rule-based fallback client — no API key required.

This provides a baseline system that works without any LLM API,
demonstrating the contrast between ML and non-ML approaches.
"""

import json
import random
from ai_service.base import BaseLLMClient

# ============================================================
# Chinese action verbs by industry
# ============================================================
ACTION_VERBS = {
    'tech': ['主导', '设计', '开发', '优化', '重构', '实现', '部署', '架构',
             '集成', '自动化', '构建', '维护', '迭代', '发布', '监控'],
    'business': ['推动', '管理', '协调', '策划', '谈判', '拓展', '运营',
                 '分析', '制定', '执行', '统筹', '提升', '降低'],
    'general': ['负责', '参与', '完成', '协助', '支持', '推进', '组织', '带领'],
}


def _pick_verbs(industry: str = 'general', count: int = 4) -> list:
    """Pick strong action verbs based on industry context."""
    verbs = ACTION_VERBS.get(industry, ACTION_VERBS['general'])
    # Rotate selection for variety
    selected = []
    for i in range(min(count, len(verbs))):
        selected.append(verbs[(i + random.randint(0, len(verbs) - 1)) % len(verbs)])
    # Use deterministic order: pick first `count` from the combined list
    strong = ACTION_VERBS.get('tech', []) + ACTION_VERBS.get('business', [])
    return strong[:count]


# ============================================================
# Template-based generators for each section
# ============================================================

def _generate_summary(resume_data: dict) -> str:
    """Generate a professional summary from template."""
    name = resume_data.get('name', '求职者')
    title = resume_data.get('title', '专业人才')
    years = resume_data.get('years_experience', '')
    city = resume_data.get('city', '')

    if years == '应届毕业生' or years == '应届':
        experience_desc = '应届毕业生，充满热情和学习能力'
    else:
        experience_desc = f'拥有{years}工作经验' if years else '拥有丰富的工作经验'

    headline = f'{experience_desc}的{title}'

    summary = (
        f'{name}，{experience_desc}，专注于{title}领域。'
        f'具备扎实的专业基础和出色的实践能力，'
        f'在工作中注重结果导向和团队协作。'
        f'期望在{title}领域持续深耕，为企业和团队创造更大价值。'
    )
    if city:
        summary = f'来自{city}的' + summary[0].lower() + summary[1:]
        headline = f'{city} | {headline}'

    result = {
        'headline': headline,
        'summary': summary,
    }
    return json.dumps(result, ensure_ascii=False)


def _generate_experience_bullets(experience: dict) -> str:
    """Generate bullet points from raw experience description using templates."""
    title = experience.get('title', '员工')
    company = experience.get('company', '公司')
    raw_desc = experience.get('raw_description', '')

    verbs = _pick_verbs('general', 4)

    if raw_desc and len(raw_desc) > 10:
        # Use the raw description to create semi-customized bullets
        bullets = [
            f'{verbs[0]}{title}相关工作，{raw_desc[:40]}，取得显著成效',
            f'{verbs[1]}团队协作与跨部门沟通，提升工作效率约30%',
            f'{verbs[2]}相关业务流程，优化工作方法，降低出错率约20%',
            f'{verbs[3]}新人培训与知识沉淀，输出技术文档{random.randint(3, 10)}篇',
        ]
    else:
        bullets = [
            f'在{company}担任{title}，{verbs[0]}核心业务工作',
            f'{verbs[1]}团队完成日常工作任务，确保项目按时交付',
            f'{verbs[2]}工作流程与效率，获得上级和同事的一致认可',
            f'{verbs[3]}部门知识库建设与经验分享',
        ]

    result = {'bullet_points': bullets}
    return json.dumps(result, ensure_ascii=False)


def _generate_skills(resume_data: dict) -> str:
    """Categorize and format skills."""
    skills = resume_data.get('skills', [])
    skill_names = []
    if isinstance(skills, list):
        for s in skills:
            if isinstance(s, dict):
                skill_names.append(s.get('name', str(s)))
            else:
                skill_names.append(str(s))

    # Simple categorization by keywords
    tech_keywords = ['python', 'java', 'c++', 'js', 'react', 'vue', 'sql', 'docker',
                     'git', 'linux', 'aws', 'html', 'css', 'php', 'node', 'go',
                     'tensorflow', 'pytorch', '机器学习', '深度学习', '数据分析']
    cert_keywords = ['证书', '认证', 'cfa', 'cpa', 'pmp', 'aws认证']
    lang_keywords = ['英语', '日语', '韩语', '法语', '普通话', '粤语']

    tech_skills = []
    cert_skills = []
    lang_skills = []
    soft_skills = []

    for s in skill_names:
        s_lower = s.lower()
        if any(kw in s_lower for kw in lang_keywords):
            lang_skills.append(f'{s}（良好）')
        elif any(kw in s_lower for kw in cert_keywords):
            cert_skills.append(s)
        elif any(kw in s_lower for kw in tech_keywords):
            tech_skills.append(f'{s}（熟练）')
        else:
            # Heuristic: non-Chinese -> tech, else soft
            has_ascii = any(ord(c) < 128 for c in s)
            if has_ascii and len(s) < 20:
                tech_skills.append(f'{s}（掌握）')
            else:
                soft_skills.append(s)

    categories = []
    if tech_skills:
        categories.append({'name': '专业技能', 'skills': tech_skills})
    if lang_skills:
        categories.append({'name': '语言能力', 'skills': lang_skills})
    if cert_skills:
        categories.append({'name': '证书资质', 'skills': cert_skills})
    if soft_skills:
        categories.append({'name': '软技能', 'skills': soft_skills})

    suggested = ['团队协作能力', '沟通表达能力', '时间管理能力']

    result = {'categories': categories, 'suggested_skills': suggested}
    return json.dumps(result, ensure_ascii=False)


def _generate_project(project: dict) -> str:
    """Generate project description from template."""
    name = project.get('name', '项目')
    role = project.get('role', '核心成员')
    tech = project.get('technologies', '相关技术')
    raw_desc = project.get('raw_description', '')

    if raw_desc:
        description = (
            f'{name}项目是一个{raw_desc[:50]}的系统/产品。'
            f'作为{role}，负责核心功能的设计与实现，'
            f'使用{tech}技术栈，项目成功上线并获得良好反馈。'
        )
    else:
        description = (
            f'{name}项目中担任{role}，'
            f'运用{tech}完成了项目的关键模块，'
            f'积累了宝贵的实践经验。'
        )

    highlights = [
        f'使用{tech}进行技术实现',
        f'在{name}项目中承担{role}角色',
        '项目成果获得了团队和用户的认可',
    ]

    result = {'description': description, 'highlights': highlights}
    return json.dumps(result, ensure_ascii=False)


def _generate_self_eval(resume_data: dict) -> str:
    """Generate self-evaluation from template."""
    title = resume_data.get('title', '专业领域')
    raw_text = resume_data.get('self_evaluation', '')
    years = resume_data.get('years_experience', '')

    if raw_text and len(raw_text) > 20:
        eval_text = (
            f'{raw_text.strip()}。'
            f'在{years if years else "过往"}的工作经历中，'
            f'始终保持着对{title}的热情和追求，'
            f'注重个人成长与团队目标的统一，'
            f'期望在未来的工作中继续深耕{title}领域，'
            f'为企业和团队带来更大价值。'
        )
    else:
        eval_text = (
            f'我是一个对{title}充满热情的专业人士，'
            f'具备{years if years else "良好"}的行业经验和扎实的专业技能。'
            f'在工作中注重细节、追求卓越，善于在团队中协作与沟通。'
            f'具备快速学习和适应新技术/新环境的能力，'
            f'期望能够在一个充满挑战的环境中不断成长。'
        )

    result = {'self_evaluation': eval_text}
    return json.dumps(result, ensure_ascii=False)


# ============================================================
# FallbackClient
# ============================================================

class FallbackClient(BaseLLMClient):
    """Rule-based fallback client that works without any API key.

    Uses template-based generation with Chinese NLP-inspired
    keyword detection and pattern matching. This serves as a
    baseline to demonstrate the value of ML approaches.
    """

    def __init__(self, api_key: str = ''):
        super().__init__(api_key)
        self._generators = {
            'summary': _generate_summary,
            'experience': _generate_experience_bullets,
            'skills': _generate_skills,
            'project': _generate_project,
            'self_eval': _generate_self_eval,
        }

    def generate(
        self,
        system_prompt: str = '',
        user_prompt: str = '',
        temperature: float = 0.4,
        max_tokens: int = 2000,
    ) -> str:
        """This is the abstract method — not used directly.
        Use generate_section() instead for fallback generation.
        """
        return '{}'

    def generate_section(self, section: str, data: dict | list) -> str:
        """Generate a specific resume section using rule-based templates.

        Args:
            section: One of 'summary', 'experience', 'skills', 'project', 'self_eval'
            data: The relevant data for that section.

        Returns:
            JSON string with the generated content.
        """
        generator = self._generators.get(section)
        if generator:
            return generator(data)
        return '{}'

    def is_available(self) -> bool:
        """Fallback client is always available."""
        return True
