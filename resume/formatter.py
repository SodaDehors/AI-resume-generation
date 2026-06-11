"""Parse and structure LLM JSON output into resume-ready format.

Handles cases where LLM output is malformed, contains markdown fences,
or is missing expected fields.
"""

import json
import re


def extract_json(text: str) -> dict:
    """Robustly extract JSON from LLM output.

    Handles:
    - Pure JSON
    - JSON inside ```json ... ``` fences
    - JSON inside ``` ... ``` fences
    - Malformed JSON with trailing commas
    - Leading/trailing text outside the JSON block

    Args:
        text: Raw text output from the LLM.

    Returns:
        Parsed dict, or empty dict on failure.
    """
    if not text:
        return {}

    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract from markdown code fences
    fence_patterns = [
        r'```json\s*([\s\S]*?)\s*```',
        r'```\s*([\s\S]*?)\s*```',
    ]
    for pattern in fence_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

    # Try to find the first { and last } and parse that
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = text[start:end + 1]
        # Fix common issues
        json_str = re.sub(r',\s*}', '}', json_str)  # trailing comma
        json_str = re.sub(r',\s*]', ']', json_str)  # trailing comma in array
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    return {}


def format_summary(llm_output: str) -> dict:
    """Format summary section from LLM output."""
    data = extract_json(llm_output)
    return {
        'headline': data.get('headline', ''),
        'summary': data.get('summary', ''),
    }


def format_experience(llm_output: str) -> dict:
    """Format work experience bullet points from LLM output."""
    data = extract_json(llm_output)
    return {
        'bullet_points': data.get('bullet_points', []),
    }


def format_skills(llm_output: str) -> dict:
    """Format skills section from LLM output."""
    data = extract_json(llm_output)
    return {
        'categories': data.get('categories', []),
        'suggested_skills': data.get('suggested_skills', []),
    }


def format_project(llm_output: str) -> dict:
    """Format project section from LLM output."""
    data = extract_json(llm_output)
    return {
        'description': data.get('description', ''),
        'highlights': data.get('highlights', []),
    }


def format_self_eval(llm_output: str) -> dict:
    """Format self-evaluation from LLM output."""
    data = extract_json(llm_output)
    return {
        'self_evaluation': data.get('self_evaluation', ''),
    }


def safe_llm_call(llm_result: str | None, default: dict | None = None) -> dict:
    """Wrapper: safely parse LLM output, returning default on failure."""
    if default is None:
        default = {}
    if not llm_result:
        return default
    try:
        return extract_json(llm_result)
    except Exception:
        return default
