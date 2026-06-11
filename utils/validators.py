"""Input validation utilities for the resume form."""

import re


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format. Returns (is_valid, error_message)."""
    if not email or not email.strip():
        return False, '邮箱不能为空'
    email = email.strip()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, '邮箱格式不正确'
    return True, ''


def validate_phone(phone: str) -> tuple[bool, str]:
    """Validate Chinese phone number. Returns (is_valid, error_message)."""
    if not phone or not phone.strip():
        return False, '手机号不能为空'
    phone = phone.strip()
    # Chinese mobile: 1[3-9]xxxxxxxxx
    pattern = r'^1[3-9]\d{9}$'
    if not re.match(pattern, phone):
        return False, '手机号格式不正确（11位中国大陆手机号）'
    return True, ''


def validate_name(name: str) -> tuple[bool, str]:
    """Validate name field. Returns (is_valid, error_message)."""
    if not name or not name.strip():
        return False, '姓名不能为空'
    name = name.strip()
    if len(name) < 2 or len(name) > 20:
        return False, '姓名长度应在2-20个字符之间'
    return True, ''


def validate_required(value: str, field_name: str) -> tuple[bool, str]:
    """Validate a required field is not empty."""
    if not value or not str(value).strip():
        return False, f'{field_name}不能为空'
    return True, ''


def validate_date_order(start: str, end: str) -> tuple[bool, str]:
    """Validate that start date is before end date.
    Dates can be in format 'YYYY-MM' or 'YYYY' or '至今' (present).
    Returns (is_valid, error_message).
    """
    if end == '至今' or not end:
        return True, ''
    if not start:
        return True, ''

    try:
        start_year = int(start[:4])
        end_year = int(end[:4])
        if start_year > end_year:
            return False, '开始日期不能晚于结束日期'

        if start_year == end_year and len(start) >= 7 and len(end) >= 7:
            start_month = int(start[5:7])
            end_month = int(end[5:7])
            if start_month > end_month:
                return False, '开始日期不能晚于结束日期'
    except (ValueError, IndexError):
        pass  # Allow fuzzy dates

    return True, ''


def sanitize_text(text: str, max_length: int = 2000) -> str:
    """Sanitize text input: strip, truncate, remove dangerous characters."""
    if not text:
        return ''
    text = text.strip()
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    if len(text) > max_length:
        text = text[:max_length]
    return text
