"""Resume generation orchestrator.

Coordinates AI calls per section, handles errors gracefully,
and assembles the final structured resume dict for template rendering.
"""

import json
import logging

from ai_service import BaseLLMClient, FallbackClient
from ai_service.prompts import (
    SUMMARY_SYSTEM, build_summary_prompt,
    EXPERIENCE_SYSTEM, build_experience_prompt,
    SKILLS_SYSTEM, build_skills_prompt,
    PROJECT_SYSTEM, build_project_prompt,
    SELF_EVAL_SYSTEM, build_self_eval_prompt,
)
from resume.formatter import (
    format_summary, format_experience, format_skills,
    format_project, format_self_eval, extract_json,
)

logger = logging.getLogger(__name__)


class ResumeGenerator:
    """Orchestrates AI-powered resume content generation.

    Uses an LLM client for AI generation or falls back to
    rule-based templates if no API key is configured.
    """

    def __init__(self, llm_client: BaseLLMClient,
                 progress_callback=None):
        self.client = llm_client
        self.use_ai = not isinstance(llm_client, FallbackClient)
        # progress_callback(current, total, message)
        self._progress = progress_callback or (lambda c, t, m: None)

    def _ai_generate(self, system: str, user: str,
                     temperature: float = 0.4) -> str:
        """Call LLM with error handling. Returns raw text or '{}'."""
        try:
            return self.client.generate(
                system_prompt=system,
                user_prompt=user,
                temperature=temperature,
                max_tokens=2000,
            )
        except Exception as e:
            logger.warning(f'LLM call failed: {e}')
            return '{}'

    def generate_summary(self, resume_data: dict) -> dict:
        """Generate professional summary and headline."""
        if self.use_ai:
            user_prompt = build_summary_prompt(resume_data)
            result = self._ai_generate(SUMMARY_SYSTEM, user_prompt, temperature=0.7)
            formatted = format_summary(result)
            if formatted.get('summary'):
                return formatted

        # Fallback
        if isinstance(self.client, FallbackClient):
            result = self.client.generate_section('summary', resume_data)
            return extract_json(result)
        return {'headline': '', 'summary': ''}

    def generate_experience(self, experience: dict) -> dict:
        """Generate bullet points for a single work experience entry."""
        if self.use_ai:
            user_prompt = build_experience_prompt(experience)
            result = self._ai_generate(EXPERIENCE_SYSTEM, user_prompt, temperature=0.3)
            formatted = format_experience(result)
            if formatted.get('bullet_points'):
                return formatted

        # Fallback
        if isinstance(self.client, FallbackClient):
            result = self.client.generate_section('experience', experience)
            return extract_json(result)
        return {'bullet_points': []}

    def generate_skills(self, resume_data: dict) -> dict:
        """Categorize and optimize skills."""
        if self.use_ai:
            user_prompt = build_skills_prompt(resume_data)
            result = self._ai_generate(SKILLS_SYSTEM, user_prompt, temperature=0.2)
            formatted = format_skills(result)
            if formatted.get('categories'):
                return formatted

        # Fallback
        if isinstance(self.client, FallbackClient):
            result = self.client.generate_section('skills', resume_data)
            return extract_json(result)
        return {'categories': [], 'suggested_skills': []}

    def generate_project(self, project: dict) -> dict:
        """Generate description for a single project."""
        if self.use_ai:
            user_prompt = build_project_prompt(project)
            result = self._ai_generate(PROJECT_SYSTEM, user_prompt, temperature=0.5)
            formatted = format_project(result)
            if formatted.get('description'):
                return formatted

        # Fallback
        if isinstance(self.client, FallbackClient):
            result = self.client.generate_section('project', project)
            return extract_json(result)
        return {'description': '', 'highlights': []}

    def generate_self_eval(self, resume_data: dict) -> dict:
        """Generate polished self-evaluation."""
        if self.use_ai:
            user_prompt = build_self_eval_prompt(resume_data)
            result = self._ai_generate(SELF_EVAL_SYSTEM, user_prompt, temperature=0.6)
            formatted = format_self_eval(result)
            if formatted.get('self_evaluation'):
                return formatted

        # Fallback
        if isinstance(self.client, FallbackClient):
            result = self.client.generate_section('self_eval', resume_data)
            return extract_json(result)
        return {'self_evaluation': ''}

    def generate_all(self, resume_data: dict) -> dict:
        """Generate the complete resume from raw user data.

        Args:
            resume_data: Raw data from the multi-step form.

        Returns:
            A fully structured resume dict ready for template rendering.
        """
        logger.info('Starting resume generation...')
        total_sections = 5 + len(resume_data.get('experience', [])) + len(resume_data.get('projects', []))
        step = 0

        # 1. Summary
        self._progress(step, total_sections, '正在生成专业摘要...')
        summary_data = self.generate_summary(resume_data)
        step += 1

        # 2. Work Experience (process each entry)
        experiences = []
        for exp in resume_data.get('experience', []):
            self._progress(step, total_sections, f'正在优化工作经历：{exp.get("company", "公司")}...')
            bullets_data = self.generate_experience(exp)
            experiences.append({
                'company': exp.get('company', ''),
                'title': exp.get('title', ''),
                'start_date': exp.get('start_date', ''),
                'end_date': exp.get('end_date', '至今'),
                'bullet_points': bullets_data.get('bullet_points', []),
            })
            step += 1

        # 3. Skills
        self._progress(step, total_sections, '正在分类整理技能...')
        skills_data = self.generate_skills(resume_data)
        step += 1

        # 4. Projects (process each entry)
        projects = []
        for proj in resume_data.get('projects', []):
            self._progress(step, total_sections, f'正在撰写项目描述：{proj.get("name", "项目")}...')
            proj_data = self.generate_project(proj)
            projects.append({
                'name': proj.get('name', ''),
                'role': proj.get('role', ''),
                'technologies': proj.get('technologies', ''),
                'description': proj_data.get('description', ''),
                'highlights': proj_data.get('highlights', []),
            })
            step += 1

        # 5. Self-evaluation
        self._progress(step, total_sections, '正在润色自我评价...')
        self_eval_data = self.generate_self_eval(resume_data)
        step += 1

        # Assemble final resume
        resume = {
            # Personal info
            'name': resume_data.get('name', ''),
            'title': resume_data.get('title', ''),
            'phone': resume_data.get('phone', ''),
            'email': resume_data.get('email', ''),
            'city': resume_data.get('city', ''),
            'years_experience': resume_data.get('years_experience', ''),
            'photo_data': resume_data.get('photo_data', ''),

            # AI-generated sections
            'headline': summary_data.get('headline', ''),
            'summary': summary_data.get('summary', ''),

            # Education (passed through as-is)
            'education': resume_data.get('education', []),

            # Work experience with AI bullet points
            'experience': experiences,

            # Skills (AI-categorized)
            'skill_categories': skills_data.get('categories', []),
            'suggested_skills': skills_data.get('suggested_skills', []),
            # Also keep raw skills for templates that want them flat
            'skills': resume_data.get('skills', []),

            # Certifications & languages (passed through)
            'certifications': resume_data.get('certifications', []),
            'languages': resume_data.get('languages', []),

            # Projects with AI descriptions
            'projects': projects,

            # Self-evaluation
            'self_evaluation': self_eval_data.get('self_evaluation', ''),

            # Career goal
            'career_goal': resume_data.get('career_goal', ''),
        }

        logger.info('Resume generation complete.')
        return resume
