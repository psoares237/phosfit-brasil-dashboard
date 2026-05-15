import streamlit as st
import plotly.express as px

from components.ui import render_kpis, chart_block
from components.charts import clean_figure

from utils.formatters import (
    fmt_currency,
    fmt_int,
    fmt_pct,
    pct_change,
)


def render(
    monthly,
    current_total,
    previous_total,
    cat,
):

    st.markdown("## Receita e Performance Comercial")

    revenue_kpis = [
        (
            "Receita Total",
            fmt_currency(current_total["receita"]),
            pct_change(
                current_total["receita"],
                previous_total["receita"],
            ),
            "período anterior",
        ),
        (
            "Pedidos",
            fmt_int(current_total["pedidos"]),
            pct_change(
                current_total["pedidos"],
                previous_total["pedidos"],
            ),
            "período anterior",
        ),
        (
            "Margem",
            fmt_pct(
                (
                    current_total["lucro"]
                    / current_total["receita"]
                    * 100
                )
                if current_total["receita"]
                else 0
            ),
            None,
            "período anterior",
        ),
    ]

    render_kpis(revenue_kpis, per_row=3)

    fig = px.line(
        monthly,
        x="Data",
        y="Receita",
        markers=True,
    )

    fig = clean_figure(fig)

    chart_block(
        "Receita Mensal",
        "Evolução da receita ao longo do período.",
        fig,
    )

    cat_top = cat.head(10)

    fig = px.bar(
        cat_top,
        x="Categoria",
        y="Receita",
        text_auto=".2s",
    )

    fig = clean_figure(fig)

    chart_block(
        "Receita por Categoria",
        "Categorias com maior geração de receita.",
        fig,
    )