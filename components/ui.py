import streamlit as st
import plotly.graph_objects as go

from utils.formatters import fmt_pct


def metric_card(title: str, value: str, delta: float | None, delta_label: str) -> None:
    if delta is None:
        delta_html = '<div class="metric-delta flat">Sem base comparável</div>'
    else:
        arrow = "▲" if delta >= 0 else "▼"
        cls = "up" if delta >= 0 else "down"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {fmt_pct(abs(delta))} vs. {delta_label}</div>'

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(items, per_row=5) -> None:
    for idx in range(0, len(items), per_row):
        row = items[idx : idx + per_row]
        cols = st.columns(len(row))

        for col, item in zip(cols, row):
            with col:
                metric_card(*item)


def section_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="section-card">
            <div class="chart-title">{title}</div>
            <div class="chart-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_block(title: str, subtitle: str, fig: go.Figure) -> None:
    st.markdown(
        f"""
        <div class="chart-card">
            <div class="chart-title">{title}</div>
            <div class="chart-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False},
        key=f"{title}_{subtitle}".replace(" ", "_").lower(),
    )