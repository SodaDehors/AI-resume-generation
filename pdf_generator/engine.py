"""PDF generation using WeasyPrint."""

import logging

logger = logging.getLogger(__name__)


def generate_pdf(html_content: str,
                 css_paths: list[str] | None = None) -> bytes:
    """Convert HTML resume to PDF bytes.

    Args:
        html_content: Complete HTML string of the rendered resume.
        css_paths: Optional list of CSS file paths to apply.

    Returns:
        PDF file as bytes, or empty bytes on failure.
    """
    try:
        from weasyprint import HTML
        html = HTML(string=html_content)
        stylesheets = css_paths if css_paths else []
        pdf_bytes = html.write_pdf(stylesheets=stylesheets)
        return pdf_bytes
    except ImportError:
        logger.error(
            'WeasyPrint not installed. '
            'Install with: pip install weasyprint'
        )
        return b''
    except Exception as e:
        logger.error(f'PDF generation failed: {e}')
        return b''


def is_pdf_available() -> bool:
    """Check if PDF generation is available."""
    try:
        import weasyprint  # noqa: F401
        return True
    except ImportError:
        return False
