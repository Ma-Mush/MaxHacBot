"""Dynamic plugin discovery and registration registry for OmniMetrics reports."""
import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type

from app.reports.base import BaseReport

logger = logging.getLogger(__name__)


class ReportRegistry:
    """Registry maintaining available BaseReport plugin instances."""

    def __init__(self) -> None:
        self._reports: Dict[str, BaseReport] = {}

    def register(self, report: BaseReport) -> None:
        """Register a report plugin instance."""
        if not report.report_id:
            raise ValueError(f"Report class {report.__class__.__name__} has no report_id defined.")
        self._reports[report.report_id] = report
        logger.info(f"Registered report plugin: '{report.report_id}' ({report.display_name})")

    def get(self, report_id: str) -> Optional[BaseReport]:
        """Retrieve report plugin by ID."""
        return self._reports.get(report_id)

    def list_reports(self) -> List[BaseReport]:
        """Return list of all registered report instances."""
        return list(self._reports.values())

    def discover(self, search_dirs: Optional[List[str]] = None) -> None:
        """Scan directory paths for Python modules containing BaseReport subclasses."""
        if search_dirs is None:
            base_dir = Path(__file__).resolve().parent.parent
            search_dirs = [
                str(base_dir / "reports" / "builtins"),
                str(base_dir / "custom_reports"),
            ]

        for directory in search_dirs:
            dir_path = Path(directory)
            if not dir_path.is_dir():
                continue

            # Ensure parent is in sys.path
            for file_path in dir_path.glob("*.py"):
                if file_path.name.startswith("__") or file_path.name.startswith("."):
                    continue

                module_name = file_path.stem
                try:
                    # Construct module import path
                    rel_to_app = file_path.resolve()
                    # Find root app path
                    app_root = dir_path.resolve()
                    while app_root.name != "app" and app_root.parent != app_root:
                        app_root = app_root.parent

                    if app_root.name == "app":
                        parent_str = str(app_root.parent)
                        if parent_str not in sys.path:
                            sys.path.insert(0, parent_str)

                        rel_parts = file_path.resolve().relative_to(app_root.parent).with_suffix("").parts
                        full_module_name = ".".join(rel_parts)
                    else:
                        full_module_name = module_name

                    module = importlib.import_module(full_module_name)

                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(obj, BaseReport)
                            and obj is not BaseReport
                            and not inspect.isabstract(obj)
                            and hasattr(obj, "report_id")
                            and obj.report_id
                        ):
                            instance = obj()
                            self.register(instance)

                except Exception as exc:
                    logger.error(f"Failed to load report plugin from {file_path}: {exc}", exc_info=True)


report_registry = ReportRegistry()
