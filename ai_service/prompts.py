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


# ============================================================
# 6. Self-Introduction Parsing — Natural Language → Structured Resume Data
# ============================================================
PARSE_INTRO_SYSTEM = SYSTEM_PERSONA + (
    '\n你擅长从自然语言自述中精准提取结构化信息。'
    '即使信息不完整或表述模糊，你也要合理推断并标注置信度。'
    '所有字段必须用中文输出，日期格式统一为YYYY-MM。'
)

PARSE_INTRO_USER_TEMPLATE = """请从以下用户的自然语言自述中，提取所有可用于简历的结构化信息。

用户自述：
{raw_text}

请输出如下JSON格式（所有字段均为必填，无法提取的字段填写空字符串或空数组）：

{{
    "name": "姓名",
    "title": "求职意向/期望职位（如无法确定，根据工作经历推断最可能的职位）",
    "phone": "手机号（原文未提及则留空）",
    "email": "邮箱（原文未提及则留空）",
    "city": "所在城市（如：北京、上海、深圳）",
    "years_experience": "工作年限区间，必须是以下之一：应届毕业生、1-3年、3-5年、5-10年、10年以上",
    "education": [
        {{
            "school": "学校全称",
            "degree": "学位（本科/硕士/博士/大专/其他）",
            "major": "专业全称",
            "start_date": "入学时间（YYYY-MM，如无法确定则填YYYY-09）",
            "end_date": "毕业时间（YYYY-MM，如无法确定则填YYYY-06）"
        }}
    ],
    "experience": [
        {{
            "company": "公司/组织全称",
            "title": "职位名称",
            "start_date": "开始时间（YYYY-MM）",
            "end_date": "结束时间（YYYY-MM 或 至今）",
            "raw_description": "1-3句话的工作内容描述，包含主要职责和成果"
        }}
    ],
    "skills": [
        {{"name": "技能名称", "level": "熟练程度（精通/熟练/掌握/了解）"}}
    ],
    "certifications": [
        {{"name": "证书名称", "issuer": "颁发机构"}}
    ],
    "languages": [
        {{"name": "语言名称", "level": "熟练程度（母语/流利/良好/基础）"}}
    ],
    "projects": [
        {{
            "name": "项目名称",
            "role": "担任角色",
            "technologies": "使用的技术栈（逗号分隔）",
            "raw_description": "1-2句话描述项目背景和你的贡献"
        }}
    ],
    "self_evaluation": "基于自述推断的个人特质描述（50-100字）",
    "career_goal": "基于自述推断的职业目标（20-50字）"
}}

重要规则：
1. 原文中明确提到的信息，直接提取
2. 原文未明确但可以合理推断的信息，填写推断值
3. 完全无法确定的信息，填写空字符串或空数组
4. 技能列表应尽可能全面，包括原文中提到的所有技能（编程语言、框架、工具、证书、语言能力等）
5. 工作年限根据工作经历的时间跨度计算
6. education、experience、projects 列表按时间顺序排列（最近的在后面）
7. 只输出JSON，不要输出任何其他内容"""
