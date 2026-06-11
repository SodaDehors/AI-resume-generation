"""Prompt templates for resume generation.

Each section has a dedicated system prompt and user-prompt template
for high-quality, targeted generation.
"""

# ============================================================
# Shared system persona (injected into every call)
# ============================================================
SYSTEM_PERSONA = (
    '你是一位资深职业简历撰写专家，拥有10年以上HR和猎头经验。'
    '你精通ATS（求职者追踪系统）优化，擅长将普通的工作描述转化为'
    '量化的、有影响力的成就陈述。你必须始终以中文输出，'
    '保持专业、简洁、有力的语言风格。所有输出必须是有效的JSON格式，'
    '不要输出JSON之外的任何内容。'
)

# ============================================================
# 1. Professional Summary
# ============================================================
SUMMARY_SYSTEM = SYSTEM_PERSONA + (
    '\n你擅长用3-4句话精准概括一个人的职业价值，'
    '突出核心竞争力、行业经验和职业亮点。'
)

SUMMARY_USER_TEMPLATE = """请为以下求职者撰写一份专业的个人摘要（3-4句话）和一句话职业标题。

个人信息：
- 姓名：{name}
- 求职意向：{title}
- 工作年限：{years_experience}
- 所在城市：{city}
- 职业目标：{career_goal}

技能标签：{skills}

工作经历摘要：{experience_summary}

请输出如下JSON格式：
{{
    "headline": "一句话职业标题（如：拥有8年经验的全栈开发工程师 | 金融科技方向）",
    "summary": "3-4句话的专业摘要，突出核心竞争力、行业经验和职业目标"
}}"""

# ============================================================
# 2. Work Experience (STAR method bullet points)
# ============================================================
EXPERIENCE_SYSTEM = SYSTEM_PERSONA + (
    '\n你特别擅长使用STAR法则（情境-任务-行动-结果）将模糊的工作描述'
    '转化为有量化数据的成就要点。每个要点必须以动词开头，'
    '包含具体的数据或成果。如果用户未提供具体数据，'
    '请根据行业标准合理推断并标注"约"。'
)

EXPERIENCE_USER_TEMPLATE = """请将以下工作经历转化为3-5条专业的量化成就要点（bullet points）。

公司：{company}
职位：{title}
工作时间：{start_date} 至 {end_date}
工作内容描述：{raw_description}

要求：
1. 每条要点以强有力的动词开头（如：主导、设计、优化、推动、实现）
2. 包含可量化的成果（数据、百分比、规模）
3. 使用STAR法则的结构
4. 每条不超过60字，保持简洁有力

请输出如下JSON格式：
{{
    "bullet_points": ["要点1", "要点2", "要点3"]
}}"""

# ============================================================
# 3. Skills Optimization
# ============================================================
SKILLS_SYSTEM = SYSTEM_PERSONA + (
    '\n你擅长将散乱的技能列表分类整理，优化技能描述，'
    '并根据求职意向推荐可能遗漏的相关技能。'
)

SKILLS_USER_TEMPLATE = """请将以下技能进行分类整理和优化。

求职意向：{title}
原始技能列表：{skills_text}

请将技能分为以下类别：
- 专业技能（编程语言、框架、工具等）
- 语言能力
- 证书资质
- 软技能

每个技能标注熟练程度：精通/熟练/掌握/了解

请输出如下JSON格式：
{{
    "categories": [
        {{
            "name": "类别名称",
            "skills": ["技能1（熟练程度）", "技能2（熟练程度）"]
        }}
    ],
    "suggested_skills": ["建议补充的技能1", "建议补充的技能2"]
}}"""

# ============================================================
# 4. Project Descriptions
# ============================================================
PROJECT_SYSTEM = SYSTEM_PERSONA + (
    '\n你擅长用2-3句话精准描述一个项目的技术深度、'
    '个人贡献和业务影响力，让招聘方一眼看出候选人的价值。'
)

PROJECT_USER_TEMPLATE = """请为以下项目撰写专业的项目描述。

项目名称：{project_name}
担任角色：{role}
使用技术：{technologies}
项目简介：{raw_description}

要求：
1. 用2-3句话描述项目背景、你的贡献和项目成果
2. 突出技术深度和业务影响力
3. 如果有量化成果（用户量、性能提升等），务必包含

请输出如下JSON格式：
{{
    "description": "2-3句话的项目概述",
    "highlights": ["技术亮点1", "技术亮点2"]
}}"""

# ============================================================
# 5. Self-Evaluation
# ============================================================
SELF_EVAL_SYSTEM = SYSTEM_PERSONA + (
    '\n你擅长将求职者零散的自我描述润色为一段专业、真诚、'
    '有说服力的自我评价，让招聘方感受到候选人的职业素养和个人特质。'
)

SELF_EVAL_USER_TEMPLATE = """请将以下自我评价润色为一段专业的自我评价（100-150字）。

原始自评：{raw_text}

求职意向：{title}
工作年限：{years_experience}

要求：
1. 语言专业但不失真诚
2. 突出职业素养、学习能力和团队协作
3. 结合求职方向，展现职业规划

请输出如下JSON格式：
{{
    "self_evaluation": "润色后的自我评价文本"
}}"""


# ============================================================
# Helper: build user prompts
# ============================================================
def build_summary_prompt(resume_data: dict) -> str:
    """Build the summary generation prompt from resume data."""
    skills = resume_data.get('skills', [])
    skills_text = '、'.join([s.get('name', str(s)) for s in skills]) if skills else '未填写'

    experiences = resume_data.get('experience', [])
    exp_parts = []
    for exp in experiences[:3]:  # top 3
        exp_parts.append(f"{exp.get('title', '')} @ {exp.get('company', '')}")
    experience_summary = '；'.join(exp_parts) if exp_parts else '无'

    return SUMMARY_USER_TEMPLATE.format(
        name=resume_data.get('name', ''),
        title=resume_data.get('title', ''),
        years_experience=resume_data.get('years_experience', ''),
        city=resume_data.get('city', ''),
        career_goal=resume_data.get('career_goal', ''),
        skills=skills_text,
        experience_summary=experience_summary,
    )


def build_experience_prompt(experience: dict) -> str:
    """Build the experience bullet-point generation prompt."""
    return EXPERIENCE_USER_TEMPLATE.format(
        company=experience.get('company', ''),
        title=experience.get('title', ''),
        start_date=experience.get('start_date', ''),
        end_date=experience.get('end_date', '至今'),
        raw_description=experience.get('raw_description', ''),
    )


def build_skills_prompt(resume_data: dict) -> str:
    """Build the skills optimization prompt."""
    skills = resume_data.get('skills', [])
    skills_text = '、'.join([s.get('name', str(s)) for s in skills]) if skills else '未填写'
    return SKILLS_USER_TEMPLATE.format(
        title=resume_data.get('title', ''),
        skills_text=skills_text,
    )


def build_project_prompt(project: dict) -> str:
    """Build the project description prompt."""
    return PROJECT_USER_TEMPLATE.format(
        project_name=project.get('name', ''),
        role=project.get('role', ''),
        technologies=project.get('technologies', ''),
        raw_description=project.get('raw_description', ''),
    )


def build_self_eval_prompt(resume_data: dict) -> str:
    """Build the self-evaluation prompt."""
    return SELF_EVAL_USER_TEMPLATE.format(
        raw_text=resume_data.get('self_evaluation', ''),
        title=resume_data.get('title', ''),
        years_experience=resume_data.get('years_experience', ''),
    )
