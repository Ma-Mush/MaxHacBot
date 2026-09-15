"""PDF rendering service using Jinja2 templates and WeasyPrint / Playwright."""
import base64
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)


class PDFRendererService:
    """Renders Jinja2 HTML templates into professional PDFs."""

    def __init__(self) -> None:
        template_dir = Path(__file__).resolve().parent.parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
        )

    def render_html(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 template into an HTML string."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    async def render_pdf(
        self,
        html_content: str,
        engine: Optional[str] = None,
    ) -> bytes:
        """Compile HTML string into PDF byte buffer."""
        target_engine = engine or settings.PDF_ENGINE

        # Try WeasyPrint
        if target_engine in ("weasyprint", "auto"):
            try:
                import weasyprint
                logger.info("Rendering PDF using WeasyPrint engine...")
                pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
                return pdf_bytes
            except Exception as exc:
                logger.warning(f"WeasyPrint rendering failed ({exc}).")
                if target_engine == "weasyprint":
                    raise

        # Try Playwright
        if target_engine in ("playwright", "auto"):
            try:
                from playwright.async_api import async_playwright
                logger.info("Rendering PDF using Playwright Chromium engine...")
                async with async_playwright() as p:
                    browser = await p.chromium.launch(
                        headless=True,
                        args=["--no-sandbox", "--disable-dev-shm-usage"],
                    )
                    page = await browser.new_page()
                    await page.set_content(html_content, wait_until="networkidle")
                    pdf_bytes = await page.pdf(
                        format="A4",
                        print_background=True,
                        margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"},
                    )
                    await browser.close()
                    return pdf_bytes
            except Exception as exc:
                logger.warning(f"Playwright rendering failed ({exc}).")
                if target_engine == "playwright":
                    raise

        raise RuntimeError(
            "No functional PDF engine found. Please install WeasyPrint dependencies "
            "or Playwright Chromium browser."
        )

    @staticmethod
    def chart_bytes_to_base64(chart_bytes: bytes) -> str:
        """Helper to encode chart PNG bytes as base64 string for HTML embedding."""
        return base64.b64encode(chart_bytes).decode("utf-8")


pdf_renderer = PDFRendererService()
