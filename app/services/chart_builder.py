"""Smart Chart Visualization Engine using Plotly & Kaleido with fallback support."""
import io
import logging
from typing import Any, Dict, List, Optional, Sequence, Union
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

# Executive Color Palette
COLOR_PALETTE = [
    "#3B82F6",  # Blue
    "#10B981",  # Emerald
    "#F59E0B",  # Amber
    "#8B5CF6",  # Purple
    "#EC4899",  # Pink
    "#06B6D4",  # Cyan
    "#F97316",  # Orange
    "#6366F1",  # Indigo
]


class ChartBuilder:
    """Builder for modern, corporate executive-grade charts."""

    def __init__(self, dark_mode: bool = False) -> None:
        self.dark_mode = dark_mode

    @property
    def theme_colors(self) -> Dict[str, str]:
        if self.dark_mode:
            return {
                "bg": "#0F172A",
                "paper": "#1E293B",
                "text": "#F8FAFC",
                "grid": "#334155",
                "muted": "#94A3B8",
            }
        return {
            "bg": "#FFFFFF",
            "paper": "#FFFFFF",
            "text": "#0F172A",
            "grid": "#E2E8F0",
            "muted": "#64748B",
        }

    def _apply_layout_defaults(
        self,
        fig: go.Figure,
        title: str,
        x_title: Optional[str] = None,
        y_title: Optional[str] = None,
        show_legend: bool = True,
    ) -> None:
        theme = self.theme_colors
        fig.update_layout(
            title={
                "text": f"<b>{title}</b>",
                "font": {"size": 18, "family": "Inter, system-ui, sans-serif", "color": theme["text"]},
                "x": 0.03,
                "y": 0.95,
            },
            font={"family": "Inter, system-ui, sans-serif", "color": theme["text"]},
            paper_bgcolor=theme["paper"],
            plot_bgcolor=theme["bg"],
            margin={"l": 50, "r": 40, "t": 60, "b": 50},
            showlegend=show_legend,
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
                "font": {"size": 11, "color": theme["muted"]},
            },
            xaxis={
                "title": {"text": x_title, "font": {"size": 12, "color": theme["muted"]}} if x_title else None,
                "showgrid": True,
                "gridcolor": theme["grid"],
                "zeroline": False,
                "tickfont": {"size": 11, "color": theme["muted"]},
            },
            yaxis={
                "title": {"text": y_title, "font": {"size": 12, "color": theme["muted"]}} if y_title else None,
                "showgrid": True,
                "gridcolor": theme["grid"],
                "zeroline": False,
                "tickfont": {"size": 11, "color": theme["muted"]},
            },
        )

    def build_line_chart(
        self,
        x_values: Sequence[Any],
        series: Dict[str, Sequence[float]],
        title: str,
        x_title: Optional[str] = None,
        y_title: Optional[str] = None,
        fill_area: bool = False,
    ) -> go.Figure:
        """Create single or multi-series time-series line / area chart."""
        fig = go.Figure()
        for idx, (name, values) in enumerate(series.items()):
            color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            fill_mode = "tozeroy" if fill_area and len(series) == 1 else None
            fig.add_trace(
                go.Scatter(
                    x=list(x_values),
                    y=list(values),
                    mode="lines+markers",
                    name=name,
                    line={"color": color, "width": 2.5, "shape": "spline"},
                    marker={"size": 5, "color": color},
                    fill=fill_mode,
                    fillcolor=f"rgba{self._hex_to_rgb(color, alpha=0.15)}" if fill_mode else None,
                )
            )
        self._apply_layout_defaults(fig, title, x_title, y_title, show_legend=(len(series) > 1))
        return fig

    def build_bar_chart(
        self,
        categories: Sequence[str],
        series: Dict[str, Sequence[float]],
        title: str,
        barmode: str = "group",  # "group" or "stack"
        x_title: Optional[str] = None,
        y_title: Optional[str] = None,
    ) -> go.Figure:
        """Create grouped or stacked bar chart for categorical metrics."""
        fig = go.Figure()
        for idx, (name, values) in enumerate(series.items()):
            color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            fig.add_trace(
                go.Bar(
                    x=list(categories),
                    y=list(values),
                    name=name,
                    marker={"color": color},
                )
            )
        self._apply_layout_defaults(fig, title, x_title, y_title, show_legend=(len(series) > 1))
        fig.update_layout(barmode=barmode)
        return fig

    def build_donut_chart(
        self,
        labels: Sequence[str],
        values: Sequence[float],
        title: str,
        hole: float = 0.55,
    ) -> go.Figure:
        """Create sleek donut chart for distribution metrics."""
        theme = self.theme_colors
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(labels),
                    values=list(values),
                    hole=hole,
                    marker={"colors": COLOR_PALETTE[: len(labels)]},
                    textinfo="label+percent",
                    textposition="inside",
                    insidetextorientation="radial",
                    hoverinfo="label+value+percent",
                )
            ]
        )
        fig.update_layout(
            title={
                "text": f"<b>{title}</b>",
                "font": {"size": 18, "family": "Inter, sans-serif", "color": theme["text"]},
                "x": 0.05,
                "y": 0.95,
            },
            paper_bgcolor=theme["paper"],
            plot_bgcolor=theme["bg"],
            margin={"l": 40, "r": 40, "t": 60, "b": 40},
            showlegend=True,
            legend={"font": {"size": 11, "color": theme["muted"]}},
        )
        return fig

    def build_kpi_card_image(
        self,
        title: str,
        value_str: str,
        delta_str: Optional[str] = None,
        is_positive: Optional[bool] = None,
        subtitle: Optional[str] = None,
    ) -> bytes:
        """Render a standalone executive KPI badge preview card as PNG."""
        # Using matplotlib to render sharp standalone card image
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3.2), dpi=150)
        bg_color = "#0F172A" if self.dark_mode else "#FFFFFF"
        card_color = "#1E293B" if self.dark_mode else "#F8FAFC"
        text_color = "#F8FAFC" if self.dark_mode else "#0F172A"
        muted_color = "#94A3B8" if self.dark_mode else "#64748B"

        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(card_color)
        ax.axis("off")

        # Draw rounded card outline
        rect = plt.Rectangle(
            (0.02, 0.04), 0.96, 0.92,
            transform=ax.transAxes,
            facecolor=card_color,
            edgecolor="#E2E8F0" if not self.dark_mode else "#334155",
            linewidth=1.5,
            clip_on=False,
            zorder=1,
        )
        ax.add_patch(rect)

        # Title
        ax.text(
            0.08, 0.78, title.upper(),
            fontsize=11, fontweight="bold", color=muted_color,
            transform=ax.transAxes, zorder=2,
        )

        # Main Value
        ax.text(
            0.08, 0.44, value_str,
            fontsize=26, fontweight="heavy", color=text_color,
            transform=ax.transAxes, zorder=2,
        )

        # Delta Badge
        if delta_str:
            badge_color = "#10B981" if is_positive else ("#EF4444" if is_positive is False else muted_color)
            prefix = "▲ " if is_positive else ("▼ " if is_positive is False else "")
            ax.text(
                0.08, 0.20, f"{prefix}{delta_str}",
                fontsize=11, fontweight="bold", color=badge_color,
                transform=ax.transAxes, zorder=2,
            )

        # Subtitle
        if subtitle:
            ax.text(
                0.92, 0.20, subtitle,
                fontsize=9, color=muted_color, horizontalalignment="right",
                transform=ax.transAxes, zorder=2,
            )

        buf = io.BytesIO()
        plt.tight_layout(pad=0.2)
        plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.getvalue()

    def fig_to_png(
        self,
        fig: go.Figure,
        width: int = 900,
        height: int = 450,
        scale: int = 2,
    ) -> bytes:
        """Export Plotly figure to high-DPI PNG bytes with fallback."""
        try:
            return fig.to_image(format="png", width=width, height=height, scale=scale)
        except Exception as exc:
            logger.warning(f"Plotly to_image export failed ({exc}), falling back to matplotlib renderer...")
            return self._plotly_to_matplotlib_fallback(fig, width, height)

    def _plotly_to_matplotlib_fallback(self, fig: go.Figure, width: int, height: int) -> bytes:
        """Graceful fallback using Matplotlib to render chart if kaleido is unavailable."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        dpi = 120
        fig_w = width / dpi
        fig_h = height / dpi
        m_fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)

        theme = self.theme_colors
        m_fig.patch.set_facecolor(theme["bg"])
        ax.set_facecolor(theme["paper"])
        ax.grid(True, linestyle="--", alpha=0.5, color=theme["grid"])

        # Plot traces
        for idx, trace in enumerate(fig.data):
            color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
            if trace.type == "scatter":
                ax.plot(trace.x, trace.y, label=trace.name or f"Series {idx+1}", color=color, linewidth=2, marker="o", markersize=4)
            elif trace.type == "bar":
                ax.bar(trace.x, trace.y, label=trace.name or f"Series {idx+1}", color=color, alpha=0.85)
            elif trace.type == "pie":
                ax.pie(trace.values, labels=trace.labels, autopct="%1.1f%%", colors=COLOR_PALETTE[:len(trace.labels)])

        title_text = fig.layout.title.text or "Chart"
        # Strip HTML tags like <b> from title
        import re
        clean_title = re.sub("<[^<]+?>", "", title_text)
        ax.set_title(clean_title, fontsize=14, fontweight="bold", color=theme["text"], pad=15)
        ax.tick_params(colors=theme["muted"])
        for spine in ax.spines.values():
            spine.set_color(theme["grid"])

        if len(fig.data) > 1 and not any(t.type == "pie" for t in fig.data):
            ax.legend(frameon=True, facecolor=theme["paper"], edgecolor=theme["grid"])

        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format="png", facecolor=m_fig.get_facecolor(), bbox_inches="tight")
        plt.close(m_fig)
        buf.seek(0)
        return buf.getvalue()

    @staticmethod
    def _hex_to_rgb(hex_code: str, alpha: float = 1.0) -> str:
        hex_code = hex_code.lstrip("#")
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return f"({r}, {g}, {b}, {alpha})"


chart_builder = ChartBuilder()
