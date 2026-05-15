from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path
from utils.formatters import (
    MESES_PT,
    month_label,
    fmt_currency,
    fmt_int,
    fmt_pct,
    pct_change,
)

from services.data_service import load_data
from services.analytics_service import grouped_sales, monthly_sales
from components.ui import metric_card, render_kpis, section_header, chart_block
from components.charts import clean_figure
from services.analytics_service import grouped_sales, monthly_sales, top_share
from pages.overview import render as render_overview
from pages.revenue import render as render_revenue
from pages.margin import render as render_margin
from pages.commercial import render as render_commercial
from pages.pricing import render as render_pricing
from pages.costs import render as render_costs
from pages.geography import render as render_geography
from pages.products import render as render_products
from pages.finance import render as render_finance
from pages.advanced_bi import render as render_advanced_bi
from pages.insights import render as render_insights
from pages.kpis import render as render_kpis_page
from pages.strategy import render as render_strategy

st.set_page_config(
    page_title="PHOSFit Brasil Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊",
)


theme_path = Path("assets/theme.css")
st.markdown(theme_path.read_text(encoding="utf-8"), unsafe_allow_html=True)


def clean_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#F7FAFC"),
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(
            font=dict(color="#DCE6F2"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        colorway=[
            "#1E6BFF",
            "#7EE787",
            "#D6B25E",
            "#60A5FA",
            "#F3DFA2",
            "#AAB7C4",
            "#F87171",
        ],
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="#AAB7C4"),
        title_font=dict(color="#DCE6F2"),
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="#AAB7C4"),
        title_font=dict(color="#DCE6F2"),
    )

    return fig


def monetary_tooltip(prefix="R$ "):
    return dict(tickprefix=prefix)


@st.cache_data


def metric_card(title: str, value: str, delta: float | None, delta_label: str) -> None:

    if delta is None:
        delta_html = '<div class="metric-delta flat">Sem base comparável</div>'
    else:
        arrow = "▲" if delta >= 0 else "▼"
        cls = "up" if delta >= 0 else "down"

        delta_html = (
            f'<div class="metric-delta {cls}">'
            f'{arrow} {fmt_pct(abs(delta))} vs. {delta_label}'
            f'</div>'
        )

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


def clean_figure(fig: go.Figure) -> go.Figure:

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#F7FAFC"
        ),
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(
            font=dict(color="#DCE6F2"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        colorway=[
            "#1E6BFF",
            "#7EE787",
            "#D6B25E",
            "#60A5FA",
            "#F3DFA2",
            "#AAB7C4",
            "#F87171",
        ],
    )

    fig.update_xaxes(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="#AAB7C4"),
        title_font=dict(color="#DCE6F2"),
    )

    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.06)",
        zerolinecolor="rgba(255,255,255,0.12)",
        linecolor="rgba(255,255,255,0.10)",
        tickfont=dict(color="#AAB7C4"),
        title_font=dict(color="#DCE6F2"),
    )

    return fig


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

st.title("PHOSFit Brasil")
st.markdown(
    """
    <div class="hero">
        <h1>Dashboard Executivo de Performance</h1>
        <p>
            Análise executiva da base de vendas com 13 abas: introdução, crescimento, margem,
            comercial, desconto, custos, geografia, produtos, finanças, BI, KPIs, insights e roadmap.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)



data = load_data("base_vendas_esportes_original.xlsx")

if data.empty:
    st.error("Não foi possível carregar dados válidos da base.")
    st.stop()

anos_disponiveis = sorted(data["Ano"].dropna().astype(int).unique().tolist())

opcoes_ano = ["Todos"] + anos_disponiveis

opcao_ano = st.sidebar.selectbox(
    "Ano",
    options=opcoes_ano,
    index=0,
)

if opcao_ano == "Todos":
    current_df = data.copy()
    previous_df = pd.DataFrame(columns=data.columns)
else:
    current_df = data[data["Ano"] == opcao_ano].copy()
    previous_df = data[data["Ano"] == opcao_ano - 1].copy()

if current_df.empty:
    st.warning("O filtro selecionado não retornou dados.")
    st.stop()


monthly = monthly_sales(current_df)
prev_monthly = monthly_sales(previous_df) if not previous_df.empty else pd.DataFrame()
seasonality = (
    data.groupby("MesNumero", as_index=False)["Receita"].mean().sort_values("MesNumero")
    if not data.empty
    else pd.DataFrame(columns=["MesNumero", "Receita"])
)
seasonality["MesNome"] = seasonality["MesNumero"].map(MESES_PT)

current_total = {
    "receita": current_df["Receita"].sum(),
    "lucro": current_df["Lucro"].sum(),
    "custo": current_df["Custo"].sum(),
    "pedidos": current_df["ID_Pedido"].nunique(),
    "qtd": current_df["Quantidade"].sum(),
    "frete": current_df["Frete"].sum(),
    "desconto_medio": current_df["Desconto_Pct"].mean(),
}

previous_total = {
    "receita": previous_df["Receita"].sum(),
    "lucro": previous_df["Lucro"].sum(),
    "custo": previous_df["Custo"].sum(),
    "pedidos": previous_df["ID_Pedido"].nunique(),
    "qtd": previous_df["Quantidade"].sum(),
    "frete": previous_df["Frete"].sum(),
    "desconto_medio": previous_df["Desconto_Pct"].mean(),
}

start_label = current_df["Data"].min().strftime("%d/%m/%Y")
end_label = current_df["Data"].max().strftime("%d/%m/%Y")
st.caption(f"Período exibido: {start_label} a {end_label}")

cat = grouped_sales(current_df, "Categoria").sort_values("Receita", ascending=False)
canal = grouped_sales(current_df, "Canal_Venda").sort_values("Receita", ascending=False)
regiao = grouped_sales(current_df, "Regiao").sort_values("Receita", ascending=False)
vendedor = grouped_sales(current_df, "Vendedor").sort_values("Receita", ascending=False)
produto = grouped_sales(current_df, "Produto").sort_values("Receita", ascending=False)
pagamento = grouped_sales(current_df, "Forma_Pagamento").sort_values("Receita", ascending=False)

produtos_full = (
    current_df.groupby("Produto", as_index=False)
    .agg(
        Receita=("Receita", "sum"),
        Lucro=("Lucro", "sum"),
        Custo=("Custo", "sum"),
        Quantidade=("Quantidade", "sum"),
        Margem=("Margem", "mean"),
        Desconto_Medio=("Desconto_Pct", "mean"),
    )
    .sort_values("Receita", ascending=False)
)
produtos_full["Lucro_Liquido"] = produtos_full["Lucro"]
produtos_full["Categoria_BCG"] = pd.qcut(
    produtos_full["Receita"].rank(method="first"),
    4,
    labels=["Abacaxi", "Interrogacao", "Vaca Leiteira", "Estrela"],
)

monthly = monthly.copy()
monthly["MesLabel"] = monthly["Data"].apply(month_label)
monthly["AnoMes"] = monthly["Data"].dt.strftime("%Y-%m")

top_revenue_product = produtos_full.iloc[0]["Produto"] if not produtos_full.empty else "Sem dados"
top_profit_product = produtos_full.sort_values("Lucro", ascending=False).iloc[0]["Produto"] if not produtos_full.empty else "Sem dados"
top_margin_product = produtos_full.sort_values("Margem", ascending=False).iloc[0]["Produto"] if not produtos_full.empty else "Sem dados"
worst_margin_product = produtos_full.sort_values("Margem", ascending=True).iloc[0]["Produto"] if not produtos_full.empty else "Sem dados"

top_category_name, top_category_share = top_share(current_df, "Categoria")
top_region_name, top_region_share = top_share(current_df, "Regiao")
top_channel_name, top_channel_share = top_share(current_df, "Canal_Venda")
top_vendor_name, top_vendor_share = top_share(current_df, "Vendedor")

tab_labels = [
    "0 - Introdução",
    "1 - Análise de Receita e Crescimento",
    "2 - Análise de Margem e Lucratividade",
    "3 - Análise Comercial",
    "4 - Análise de Preço e Desconto",
    "5 - Análise de Custos e Eficiência Operacional",
    "6 - Análise Geográfica",
    "7 - Análise de Produtos",
    "8 - Análise Financeira Executiva",
    "9 - Análises Avançadas (BI)",
    "10 - Principais KPIs Recomendados",
    "11 - Insights Estratégicos",
    "12 - Evolução Recomendada",
]

tabs = st.tabs(tab_labels)


with tabs[0]:
    intro_kpis = [
        ("Receita Total", fmt_currency(current_total["receita"]), pct_change(current_total["receita"], previous_total["receita"]), "período anterior"),
        ("Lucro Total", fmt_currency(current_total["lucro"]), pct_change(current_total["lucro"], previous_total["lucro"]), "período anterior"),
        ("Margem de Lucro", fmt_pct((current_total["lucro"] / current_total["receita"] * 100) if current_total["receita"] else 0), None, "período anterior"),
        ("Ticket Médio", fmt_currency(current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), None, "período anterior"),
        ("Total de Pedidos", fmt_int(current_total["pedidos"]), pct_change(current_total["pedidos"], previous_total["pedidos"]), "período anterior"),
    ]

    render_overview(intro_kpis)


with tabs[1]:
    render_revenue(
        monthly,
        current_total,
        previous_total,
        cat,
    )

with tabs[2]:
    render_margin(
        monthly,
        current_total,
        previous_total,
        cat,
        vendedor,
        produto,
        current_df,
        top_profit_product,
    )

with tabs[3]:
    render_commercial(
        current_df,
        current_total,
        previous_total,
        canal,
        vendedor,
        regiao,
        top_channel_name,
        top_channel_share,
        top_vendor_name,
        top_vendor_share,
    )

with tabs[4]:
    render_pricing(
        current_df,
        current_total,
        previous_total,
        cat,
        canal,
        vendedor,
    )


with tabs[5]:
    render_costs(
        current_df,
        current_total,
        previous_total,
        regiao,
        canal,
        monthly,
    )


with tabs[6]:
    render_geography(
        regiao,
        current_total,
        top_region_name,
        top_region_share,
    )

with tabs[7]:
    render_products(
        produtos_full,
        top_revenue_product,
        top_profit_product,
        top_margin_product,
        worst_margin_product,
    )

        
with tabs[8]:
    render_finance(
        monthly,
        current_total,
    )


with tabs[9]:
    render_advanced_bi(
        monthly,
        seasonality,
    )    

with tabs[10]:
    render_kpis_page(
        current_total,
        previous_total,
        monthly,
    )

with tabs[11]:
    render_insights(
        current_total,
        monthly,
        cat,
        vendedor,
    )

with tabs[12]:
    render_strategy(
        current_total,
        monthly,
        cat,
        produto,
    )




