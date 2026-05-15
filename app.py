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

st.set_page_config(
    page_title="PHOSFit Brasil Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊",
)


theme_path = Path("assets/theme.css")
st.markdown(theme_path.read_text(encoding="utf-8"), unsafe_allow_html=True)


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


def top_share(df: pd.DataFrame, column: str) -> tuple[str, float]:
    grouped = df.groupby(column, as_index=False)["Receita"].sum().sort_values("Receita", ascending=False)
    if grouped.empty:
        return "Sem dados", 0
    top_name = grouped.iloc[0][column]
    share = grouped.iloc[0]["Receita"] / grouped["Receita"].sum() * 100 if grouped["Receita"].sum() else 0
    return str(top_name), share





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
    section_header(
        "Introdução",
        "Visao geral do painel, resumo dos KPIs e leitura executiva da base real.",
    )

    intro_kpis = [
        ("Receita Total", fmt_currency(current_total["receita"]), pct_change(current_total["receita"], previous_total["receita"]), "período anterior"),
        ("Lucro Total", fmt_currency(current_total["lucro"]), pct_change(current_total["lucro"], previous_total["lucro"]), "período anterior"),
        ("Margem de Lucro", fmt_pct((current_total["lucro"] / current_total["receita"] * 100) if current_total["receita"] else 0), pct_change((current_total["lucro"] / current_total["receita"] * 100) if current_total["receita"] else 0, (previous_total["lucro"] / previous_total["receita"] * 100) if previous_total["receita"] else None), "período anterior"),
        ("Ticket Médio", fmt_currency(current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), pct_change((current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), (previous_total["receita"] / previous_total["pedidos"] if previous_total["pedidos"] else 0)), "período anterior"),
        ("Total de Pedidos", fmt_int(current_total["pedidos"]), pct_change(current_total["pedidos"], previous_total["pedidos"]), "período anterior"),
    ]
    render_kpis(intro_kpis)

    col_a, col_b = st.columns(2)
    with col_a:
        fig = px.line(monthly, x="Data", y="Receita", markers=True)
        fig.add_scatter(x=monthly["Data"], y=monthly["Lucro"], mode="lines+markers", name="Lucro", line=dict(color="#2dd4bf", width=3))
        fig.update_traces(line=dict(color="#60a5fa", width=3), name="Receita", selector=dict(name=""))
        fig.update_layout(height=360, hovermode="x unified", legend=dict(orientation="h", y=1.02, x=0))
        fig.update_yaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block(
            "Evolução mensal de Receita e Lucro",
            "Resumo visual da operação ao longo do período filtrado.",
            fig,
        )
    with col_b:
        fig = px.bar(cat.head(8), x="Receita", y="Categoria", orientation="h", text_auto=".2s")
        fig.update_traces(hovertemplate="Categoria: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_xaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block(
            "Categorias que mais geram receita",
            "Leitura rápida de concentração comercial por categoria.",
            fig,
        )

    st.markdown(
        """
        <div class="callout">
            <div class="callout-title">Como ler este painel</div>
            <div>
                As análises usam apenas a base carregada. Onde o dado não existe hoje
                (como ID de cliente, conversão ou churn), o dashboard mostra apenas a
                recomendação de evolução futura, sem inventar indicador.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with tabs[1]:
    section_header(
        "Análise de Receita e Crescimento",
        "Receita total, evolução temporal, sazonalidade e concentração de faturamento.",
    )
    intro_kpis = [
        ("Receita Total", fmt_currency(current_total["receita"]), pct_change(current_total["receita"], previous_total["receita"]), "período anterior"),
        ("Receita / Pedido", fmt_currency(current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), pct_change((current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), (previous_total["receita"] / previous_total["pedidos"] if previous_total["pedidos"] else 0)), "período anterior"),
        ("Crescimento MoM", fmt_pct(monthly["MoM_Receita"].dropna().iloc[-1]) if monthly["MoM_Receita"].dropna().any() else "n/d", None, "mês anterior"),
        ("Receita Acumulada", fmt_currency(monthly["Acumulado_Receita"].iloc[-1]), None, "período"),
        ("Share da maior categoria", fmt_pct(top_category_share), None, top_category_name),
    ]
    render_kpis(intro_kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=monthly["Data"], y=monthly["Receita"], mode="lines+markers", name="Receita", line=dict(color="#60a5fa", width=3)), secondary_y=False)
        fig.add_trace(go.Scatter(x=monthly["Data"], y=monthly["Lucro"], mode="lines+markers", name="Lucro", line=dict(color="#2dd4bf", width=3)), secondary_y=True)
        fig.update_layout(height=380, hovermode="x unified", legend=dict(orientation="h", y=1.03, x=0))
        fig.update_yaxes(title_text="Receita", secondary_y=False, tickprefix="R$ ")
        fig.update_yaxes(title_text="Lucro", secondary_y=True, tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Receita vs Lucro", "Comparativo mensal com dois eixos.", fig)
    with c2:
        fig = px.line(monthly, x="Data", y="Acumulado_Receita", markers=True, line_shape="spline")
        fig.update_traces(line=dict(color="#a78bfa", width=3), hovertemplate="%{x|%b/%Y}<br>Acumulado: R$ %{y:,.2f}<extra></extra>")
        fig.update_layout(height=380)
        fig.update_yaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Receita acumulada", "Permite ver a velocidade de geração de faturamento.", fig)

    c3, c4 = st.columns(2)
    with c3:
        season = seasonality.copy()
        fig = px.bar(season, x="MesNome", y="Receita", text_auto=".2s")
        fig.update_traces(hovertemplate="Mês: %{x}<br>Receita média: R$ %{y:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_yaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Sazonalidade", "Receita média por mês do ano.", fig)
    with c4:
        fig = px.bar(cat.head(10).sort_values("Receita"), x="Receita", y="Categoria", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Categoria: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Receita por categoria", "Concentração de receita por portfólio.", fig)


with tabs[2]:
    section_header(
        "Análise de Margem e Lucratividade",
        "Lucro, margem bruta, rentabilidade e erosão de resultado por dimensão.",
    )
    kpis = [
        ("Lucro Total", fmt_currency(current_total["lucro"]), pct_change(current_total["lucro"], previous_total["lucro"]), "período anterior"),
        ("Margem Bruta", fmt_pct((current_total["lucro"] / current_total["receita"] * 100) if current_total["receita"] else 0), pct_change((current_total["lucro"] / current_total["receita"] * 100) if current_total["receita"] else 0, (previous_total["lucro"] / previous_total["receita"] * 100) if previous_total["receita"] else None), "período anterior"),
        ("Lucro / Pedido", fmt_currency(current_total["lucro"] / current_total["pedidos"] if current_total["pedidos"] else 0), None, "pedido"),
        ("Margem Líquida Est.", fmt_pct((current_df["Lucro_Liquido_Estimado"].sum() / current_total["receita"] * 100) if current_total["receita"] else 0), None, "receita"),
        ("Produto mais lucrativo", top_profit_product, None, "base atual"),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(cat.sort_values("Margem"), x="Margem", y="Categoria", orientation="h", text_auto=".1f")
        fig.update_xaxes(title_text="Margem (%)")
        fig.update_traces(hovertemplate="Categoria: %{y}<br>Margem: %{x:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Margem por categoria", "Categorias mais e menos rentáveis.", fig)
    with c2:
        fig = px.bar(vendedor.head(10).sort_values("Lucro"), x="Lucro", y="Vendedor", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Vendedor: %{y}<br>Lucro: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Lucro por vendedor", "Eficiência comercial em termos de resultado.", fig)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.area(monthly, x="Data", y="Margem", line_shape="spline")
        fig.update_traces(line=dict(color="#a78bfa", width=3), fillcolor="rgba(167,139,250,0.22)", hovertemplate="%{x|%b/%Y}<br>Margem: %{y:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_yaxes(title_text="Margem (%)")
        clean_figure(fig)
        chart_block("Margem ao longo do tempo", "Evolução da lucratividade percentual.", fig)
    with c4:
        margin_top = produto.sort_values("Margem", ascending=False).head(10).sort_values("Margem")
        fig = px.bar(margin_top, x="Margem", y="Produto", orientation="h", text_auto=".1f")
        fig.update_traces(hovertemplate="Produto: %{y}<br>Margem: %{x:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Margem por produto", "Produtos que vendem muito ou lucram muito.", fig)


with tabs[3]:
    section_header(
        "Análise Comercial",
        "Ticket médio, volume, canais e performance operacional de vendas.",
    )
    kpis = [
        ("Ticket Médio", fmt_currency(current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), pct_change((current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), (previous_total["receita"] / previous_total["pedidos"] if previous_total["pedidos"] else 0)), "período anterior"),
        ("Pedidos", fmt_int(current_total["pedidos"]), pct_change(current_total["pedidos"], previous_total["pedidos"]), "período anterior"),
        ("Quantidade Vendida", fmt_int(current_total["qtd"]), None, "unidades"),
        ("Canal líder", top_channel_name, None, fmt_pct(top_channel_share)),
        ("Vendedor líder", top_vendor_name, None, fmt_pct(top_vendor_share)),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(canal.sort_values("Receita"), x="Receita", y="Canal_Venda", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Canal: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Receita por canal", "Comparação entre canais de venda.", fig)
    with c2:
        fig = px.bar(vendedor.head(10).sort_values("Receita"), x="Receita", y="Vendedor", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Vendedor: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Receita por vendedor", "Eficiência comercial individual.", fig)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(regiao.sort_values("Pedidos"), x="Pedidos", y="Regiao", orientation="h", text_auto=".2s")
        fig.update_traces(hovertemplate="Região: %{y}<br>Pedidos: %{x:,.0f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Pedidos por região", "Volume de atuação regional.", fig)
    with c4:
        fig = px.histogram(current_df, x="Quantidade", nbins=20)
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Distribuição da quantidade vendida", "Leitura do comportamento de volume por linha.", fig)


with tabs[4]:
    section_header(
        "Análise de Preço e Desconto",
        "Desconto médio, impacto na margem e oportunidades de política comercial.",
    )
    desconto_medio = current_df["Desconto_Pct"].mean()
    pedidos_com_desconto = (current_df["Desconto_Rate"] > 0).sum()
    share_desconto = pedidos_com_desconto / len(current_df) * 100 if len(current_df) else 0
    desconto_total_estimado = current_df["Desconto_Valor_Estimado"].sum()
    preco_bruto_total = current_df["Preco_Bruto_Estimado"].sum()

    kpis = [
        ("Desconto Médio", fmt_pct(desconto_medio), pct_change(desconto_medio, previous_total["desconto_medio"]), "período anterior"),
        ("Pedidos com desconto", fmt_int(pedidos_com_desconto), None, fmt_pct(share_desconto)),
        ("Receita bruta estimada", fmt_currency(preco_bruto_total), None, "antes do desconto"),
        ("Valor concedido", fmt_currency(desconto_total_estimado), None, "estimado"),
        ("Impacto na margem", fmt_pct((desconto_total_estimado / current_total["receita"] * 100) if current_total["receita"] else 0), None, "receita"),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(cat.sort_values("Desconto_Medio"), x="Desconto_Medio", y="Categoria", orientation="h", text_auto=".1f")
        fig.update_traces(hovertemplate="Categoria: %{y}<br>Desconto médio: %{x:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Desconto médio por categoria", "Categoria mais sensível a política comercial.", fig)
    with c2:
        fig = px.bar(canal.sort_values("Desconto_Medio"), x="Desconto_Medio", y="Canal_Venda", orientation="h", text_auto=".1f")
        fig.update_traces(hovertemplate="Canal: %{y}<br>Desconto médio: %{x:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Desconto médio por canal", "Canais com maior dependência de incentivo.", fig)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.scatter(
            current_df,
            x="Desconto_Pct",
            y="Margem",
            color="Canal_Venda",
            size="Receita",
            hover_data=["Categoria", "Produto", "Vendedor"],
            opacity=0.7,
        )
        fig.update_layout(height=360, legend_title_text="")
        clean_figure(fig)
        chart_block("Desconto x margem", "Mostra a erosão de margem conforme o desconto aumenta.", fig)
    with c4:
        sim = current_df.groupby("Vendedor", as_index=False).agg(Desconto=("Desconto_Pct", "mean"), Receita=("Receita", "sum"), Lucro=("Lucro", "sum")).sort_values("Desconto", ascending=False).head(10)
        fig = px.bar(sim, x="Desconto", y="Vendedor", orientation="h", text_auto=".1f")
        fig.update_traces(hovertemplate="Vendedor: %{y}<br>Desconto médio: %{x:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Desconto por vendedor", "Ajuda a identificar dependência de incentivo.", fig)

    st.markdown(
        """
        <div class="callout">
            <div class="callout-title">Simulação de cenário</div>
            <div>
                A coluna de desconto permite estimar receita bruta antes de desconto e o valor concedido.
                Esse cálculo é derivado da base, então não inventa cenário fora dos dados. Se quiser,
                na próxima etapa eu posso transformar isso em uma calculadora de preço com sliders.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with tabs[5]:
    section_header(
        "Análise de Custos e Eficiência Operacional",
        "Custo total, frete, peso logístico e lucro líquido estimado.",
    )
    custo_revenue = (current_total["custo"] / current_total["receita"] * 100) if current_total["receita"] else 0
    frete_revenue = (current_total["frete"] / current_total["receita"] * 100) if current_total["receita"] else 0
    lucro_liquido = current_df["Lucro_Liquido_Estimado"].sum()

    kpis = [
        ("Custo Total", fmt_currency(current_total["custo"]), pct_change(current_total["custo"], previous_total["custo"]), "período anterior"),
        ("Custo / Receita", fmt_pct(custo_revenue), None, "eficiência"),
        ("Frete Total", fmt_currency(current_total["frete"]), None, "período"),
        ("Frete / Receita", fmt_pct(frete_revenue), None, "eficiência"),
        ("Lucro líquido est.", fmt_currency(lucro_liquido), None, "Lucro - Frete"),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(regiao.sort_values("Frete_Medio"), x="Frete_Medio", y="Regiao", orientation="h", text_auto=".2f")
        fig.update_traces(hovertemplate="Região: %{y}<br>Frete médio: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_xaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Frete médio por região", "Regiões mais caras de operar.", fig)
    with c2:
        fig = px.bar(canal.sort_values("Frete_Medio"), x="Frete_Medio", y="Canal_Venda", orientation="h", text_auto=".2f")
        fig.update_traces(hovertemplate="Canal: %{y}<br>Frete médio: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_xaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Frete médio por canal", "Canais com maior peso de distribuição.", fig)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.line(monthly, x="Data", y="Custo", markers=True)
        fig.update_traces(line=dict(color="#fb923c", width=3), hovertemplate="%{x|%b/%Y}<br>Custo: R$ %{y:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_yaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Custo ao longo do tempo", "Acompanha a estrutura de custos mês a mês.", fig)
    with c4:
        unprofitable = current_df.assign(Lucro_Liquido_Estimado=current_df["Lucro_Liquido_Estimado"]).groupby("Produto", as_index=False)["Lucro_Liquido_Estimado"].sum().sort_values("Lucro_Liquido_Estimado").head(10)
        fig = px.bar(unprofitable, x="Lucro_Liquido_Estimado", y="Produto", orientation="h", text_auto=".2s")
        fig.update_traces(hovertemplate="Produto: %{y}<br>Lucro líquido est.: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_xaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Produtos menos eficientes", "Produtos que mais pressionam o resultado operacional.", fig)


with tabs[6]:
    section_header(
        "Análise Geográfica",
        "Receita, lucro, ticket e margem por região com visão de concentração.",
    )
    kpis = [
        ("Região líder", top_region_name, None, fmt_pct(top_region_share)),
        ("Receita regional", fmt_currency(regiao["Receita"].sum()), None, "base filtrada"),
        ("Lucro regional", fmt_currency(regiao["Lucro"].sum()), None, "base filtrada"),
        ("Ticket regional", fmt_currency(current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), None, "visao geral"),
        ("Margem regional média", fmt_pct(regiao["Margem"].mean()), None, "média simples"),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(regiao.sort_values("Receita"), x="Receita", y="Regiao", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Região: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Receita por região", "Mercados que mais sustentam faturamento.", fig)
    with c2:
        fig = px.bar(regiao.sort_values("Lucro"), x="Lucro", y="Regiao", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Região: %{y}<br>Lucro: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Lucro por região", "Regiões mais rentáveis.", fig)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(regiao.sort_values("Margem"), x="Margem", y="Regiao", orientation="h", text_auto=".1f")
        fig.update_traces(hovertemplate="Região: %{y}<br>Margem: %{x:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Margem por região", "Comparação da eficiência regional.", fig)
    with c4:
        fig = px.bar(regiao.sort_values("Pedidos"), x="Pedidos", y="Regiao", orientation="h", text_auto=".2s")
        fig.update_traces(hovertemplate="Região: %{y}<br>Pedidos: %{x:,.0f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Volume de pedidos por região", "Leitura de alcance comercial regional.", fig)


with tabs[7]:
    section_header(
        "Análise de Produtos",
        "Portfólio, produtos campeões, rentabilidade e curva ABC simplificada.",
    )
    abc = produtos_full.copy()
    abc["Share_Receita"] = abc["Receita"] / abc["Receita"].sum() if abc["Receita"].sum() else 0
    abc["Share_Cum"] = abc["Share_Receita"].cumsum()
    abc["ABC"] = pd.cut(
        abc["Share_Cum"],
        bins=[0, 0.8, 0.95, 1.0],
        labels=["A", "B", "C"],
        include_lowest=True,
    )

    kpis = [
        ("Mais vendido", top_revenue_product, None, "receita"),
        ("Mais lucrativo", top_profit_product, None, "lucro"),
        ("Maior margem", top_margin_product, None, "margem"),
        ("Menor margem", worst_margin_product, None, "risco"),
        ("Classe A", fmt_int((abc["ABC"] == "A").sum()), None, "produtos"),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(produtos_full.head(10).sort_values("Receita"), x="Receita", y="Produto", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Produto: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Top 10 produtos por receita", "Itens que mais carregam o faturamento.", fig)
    with c2:
        fig = px.bar(produtos_full.sort_values("Lucro").head(10), x="Lucro", y="Produto", orientation="h", text_auto=".2s")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Produto: %{y}<br>Lucro: R$ %{x:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Produtos menos lucrativos", "Pontos de atenção do portfólio.", fig)

    c3, c4 = st.columns(2)
    with c3:
        bubble = abc.head(20).copy()

        fig = px.scatter(
            bubble,
            x="Receita",
            y="Lucro",
            size="Quantidade",
            color="ABC",
            hover_name="Produto",
)

        fig.update_layout(height=360, legend_title_text="")
        fig.update_xaxes(tickprefix="R$ ")
        fig.update_yaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Matriz BCG simplificada", "Receita x lucro com classificação A/B/C.", fig)
    with c4:
        fig = px.bar(abc.groupby("ABC", as_index=False)["Receita"].sum(), x="ABC", y="Receita", text_auto=".2s")
        fig.update_yaxes(tickprefix="R$ ")
        fig.update_traces(hovertemplate="Classe: %{x}<br>Receita: R$ %{y:,.2f}<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        clean_figure(fig)
        chart_block("Curva ABC de receita", "Estratificação do portfólio por valor.", fig)


with tabs[8]:
    section_header(
        "Análise Financeira Executiva",
        "Indicadores sintéticos de margem, crescimento e eficiência financeira.",
    )
    first_month = monthly.iloc[0]
    last_month = monthly.iloc[-1]
    cagr = ((last_month["Receita"] / first_month["Receita"]) ** (12 / max(len(monthly) - 1, 1)) - 1) * 100 if first_month["Receita"] > 0 and len(monthly) > 1 else None
    yoy = None
    if len(monthly) >= 13:
        yoy = pct_change(monthly.iloc[-1]["Receita"], monthly.iloc[-13]["Receita"])
    avg_mom = monthly["MoM_Receita"].mean()
    markup = ((current_total["receita"] - current_total["custo"]) / current_total["custo"] * 100) if current_total["custo"] else 0
    rent_per_order = current_total["lucro"] / current_total["pedidos"] if current_total["pedidos"] else 0

    kpis = [
        ("Margem Bruta", fmt_pct((current_total["lucro"] / current_total["receita"] * 100) if current_total["receita"] else 0), None, "receita"),
        ("Markup", fmt_pct(markup), None, "receita x custo"),
        ("CAGR simplificado", fmt_pct(cagr) if cagr is not None else "n/d", None, "período"),
        ("Crescimento YoY", fmt_pct(yoy) if yoy is not None else "n/d", None, "últimos 12 meses"),
        ("Rentabilidade por pedido", fmt_currency(rent_per_order), None, "lucro / pedido"),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(monthly, x="Data", y="MoM_Receita", markers=True)
        fig.update_traces(line=dict(color="#60a5fa", width=3), hovertemplate="%{x|%b/%Y}<br>MoM: %{y:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_yaxes(title_text="MoM (%)")
        clean_figure(fig)
        chart_block("Crescimento mensal de receita", "Taxa mês contra mês.", fig)
    with c2:
        fig = px.line(monthly, x="Data", y="MoM_Lucro", markers=True)
        fig.update_traces(line=dict(color="#2dd4bf", width=3), hovertemplate="%{x|%b/%Y}<br>MoM: %{y:.1f}%<extra></extra>")
        fig.update_layout(height=360, showlegend=False)
        fig.update_yaxes(title_text="MoM (%)")
        clean_figure(fig)
        chart_block("Crescimento mensal de lucro", "Verifica se a operação melhora junto com a receita.", fig)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.area(monthly, x="Data", y="Acumulado_Lucro")
        fig.update_traces(line=dict(color="#a78bfa", width=3), fillcolor="rgba(167,139,250,0.22)")
        fig.update_layout(height=360, showlegend=False)
        fig.update_yaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Lucro acumulado", "Performance financeira consolidada.", fig)
    with c4:
        fig = px.line(monthly, x="Data", y="Margem", markers=True)
        fig.update_traces(line=dict(color="#fb923c", width=3))
        fig.update_layout(height=360, showlegend=False)
        fig.update_yaxes(title_text="Margem (%)")
        clean_figure(fig)
        chart_block("Margem mensal", "Leitura executiva de rentabilidade ao longo do tempo.", fig)

    st.markdown(
        f"""
        <div class="callout">
            <div class="callout-title">Resumo financeiro</div>
            <div>
                Crescimento médio mensal de receita: <b>{fmt_pct(avg_mom) if pd.notna(avg_mom) else 'n/d'}</b>.
                CAGR simplificado no período: <b>{fmt_pct(cagr) if cagr is not None else 'n/d'}</b>.
                O indicador de YoY é exibido apenas quando a série cobre pelo menos 13 meses.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with tabs[9]:
    section_header(
        "Análises Avançadas (Business Intelligence)",
        "Projeções exploratórias, sazonalidade profunda e roadmap de evolução analítica.",
    )
    horizon = min(3, len(monthly))
    forecast_base = monthly["Receita"].tail(min(3, len(monthly))).mean() if len(monthly) else 0
    forecast_next = [forecast_base * (1 + x) for x in (0.00, 0.03, 0.06)]
    future_dates = pd.date_range(monthly["Data"].iloc[-1] + pd.offsets.MonthBegin(1), periods=3, freq="MS") if len(monthly) else []

    kpis = [
        ("Forecast exploratório", fmt_currency(forecast_next[0]) if forecast_next else "n/d", None, "próximo mês"),
        ("Tendência curta", fmt_currency(forecast_base) if forecast_base else "n/d", None, "média 3 meses"),
        ("Sazonalidade detectável", "Sim" if seasonality["Receita"].notna().any() else "Não", None, "base histórica"),
        ("LTV / Churn", "Futuro", None, "depende de cliente"),
        ("Previsão de ruptura", "Futuro", None, "depende de estoque"),
    ]
    render_kpis(kpis)

    c1, c2 = st.columns(2)
    with c1:
        heat = monthly.pivot_table(index="Ano", columns="MesNumero", values="Receita", aggfunc="sum").reindex(columns=range(1, 13))
        fig = px.imshow(
            heat,
            aspect="auto",
            color_continuous_scale=["#0f172a", "#1d4ed8", "#60a5fa", "#a78bfa"],
            labels=dict(x="Mês", y="Ano", color="Receita"),
        )
        fig.update_layout(height=360, coloraxis_colorbar=dict(title="R$"))
        clean_figure(fig)
        chart_block("Heatmap anual de receita", "Mostra padrões de sazonalidade por ano e mês.", fig)
    with c2:
        forecast_df = pd.DataFrame({"Data": list(monthly["Data"]) + list(future_dates), "Receita": list(monthly["Receita"]) + forecast_next + [np.nan] * max(0, 3 - len(forecast_next))})
        fig = px.line(monthly, x="Data", y="Receita", markers=True)
        if len(future_dates):
            fig.add_scatter(x=future_dates, y=forecast_next, mode="lines+markers", name="Forecast exploratório", line=dict(color="#fb923c", width=3, dash="dash"))
        fig.update_layout(height=360, showlegend=True, legend=dict(orientation="h", y=1.03, x=0))
        fig.update_yaxes(tickprefix="R$ ")
        clean_figure(fig)
        chart_block("Projeção exploratória", "Estimativa simples baseada na média dos últimos 3 meses.", fig)

    st.markdown(
        """
        <div class="callout">
            <div class="callout-title">Possibilidades futuras</div>
            <div>
                Com ID de cliente, a base passa a permitir LTV, churn, frequência de recompra e perfil de consumo.
                Com dados de estoque, abre espaço para previsão de ruptura e otimização de abastecimento.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with tabs[10]:
    section_header(
        "Principais KPIs Recomendados para o Dashboard Executivo",
        "Catálogo de indicadores prioritários, com os valores atuais da base.",
    )
    kpis = [
        ("Receita Total", fmt_currency(current_total["receita"]), None, "financeiro"),
        ("Lucro Total", fmt_currency(current_total["lucro"]), None, "financeiro"),
        ("Margem Bruta", fmt_pct((current_total["lucro"] / current_total["receita"] * 100) if current_total["receita"] else 0), None, "financeiro"),
        ("Crescimento Mensal", fmt_pct(monthly["MoM_Receita"].dropna().mean()) if monthly["MoM_Receita"].dropna().any() else "n/d", None, "financeiro"),
        ("Ticket Médio", fmt_currency(current_total["receita"] / current_total["pedidos"] if current_total["pedidos"] else 0), None, "comercial"),
        ("Desconto Médio", fmt_pct(current_total["desconto_medio"]), None, "comercial"),
        ("Frete Médio", fmt_currency(current_df["Frete"].mean()), None, "operacional"),
        ("Pedidos", fmt_int(current_total["pedidos"]), None, "comercial"),
        ("Receita por Canal", top_channel_name, None, fmt_pct(top_channel_share)),
        ("Receita por Região", top_region_name, None, fmt_pct(top_region_share)),
        ("Receita por Vendedor", top_vendor_name, None, fmt_pct(top_vendor_share)),
        ("Produto Mais Vendido", top_revenue_product, None, "portfólio"),
    ]
    render_kpis(kpis, per_row=4)

    st.markdown(
        """
        <div class="callout">
            <div class="callout-title">Leitura recomendada</div>
            <div>
                Se eu fosse resumir a gestão executiva em poucos blocos, eu priorizaria: receita, margem,
                ticket médio, desconto, frete, canal, região, vendedor e produto. Esses indicadores já cobrem
                praticamente toda a tomada de decisão comercial e financeira da base atual.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with tabs[11]:
    section_header(
        "Insights Estratégicos",
        "Resumo narrativo gerado a partir dos dados reais da base.",
    )
    concentration = {
        "Categoria": top_category_share,
        "Região": top_region_share,
        "Canal": top_channel_share,
        "Vendedor": top_vendor_share,
    }
    best_month = monthly.sort_values("Receita", ascending=False).iloc[0]
    worst_month = monthly.sort_values("Receita", ascending=True).iloc[0]
    top_discount_vendor = vendedor.sort_values("Desconto_Medio", ascending=False).iloc[0]["Vendedor"]
    best_profit_region = regiao.sort_values("Lucro", ascending=False).iloc[0]["Regiao"]

    st.markdown(
        f"""
        <div class="mini-grid">
            <div class="mini-box">
                <div class="mini-label">Mês de maior receita</div>
                <div class="mini-value">{month_label(best_month["Data"])}</div>
                <div class="mini-note">{fmt_currency(best_month["Receita"])}</div>
            </div>
            <div class="mini-box">
                <div class="mini-label">Mês de menor receita</div>
                <div class="mini-value">{month_label(worst_month["Data"])}</div>
                <div class="mini-note">{fmt_currency(worst_month["Receita"])}</div>
            </div>
            <div class="mini-box">
                <div class="mini-label">Categoria mais relevante</div>
                <div class="mini-value">{top_category_name}</div>
                <div class="mini-note">Share: {fmt_pct(top_category_share)}</div>
            </div>
            <div class="mini-box">
                <div class="mini-label">Região mais lucrativa</div>
                <div class="mini-value">{best_profit_region}</div>
                <div class="mini-note">{fmt_currency(regiao.sort_values("Lucro", ascending=False).iloc[0]["Lucro"])}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Principais observações")
    st.write(
        [
            f"A maior concentração de receita está em {top_category_name} ({fmt_pct(top_category_share)} da receita da base filtrada).",
            f"O canal dominante hoje é {top_channel_name}, com {fmt_pct(top_channel_share)} da receita.",
            f"A região {top_region_name} lidera o faturamento, mas a região mais lucrativa é {best_profit_region}.",
            f"O vendedor com maior desconto médio é {top_discount_vendor}, o que merece atenção para erosao de margem.",
            f"O produto mais lucrativo é {top_profit_product}, enquanto o de menor margem é {worst_margin_product}.",
        ]
    )

    st.markdown("### Concentração de dependência")
    dep = pd.DataFrame(
        {
            "Dimensão": ["Categoria", "Região", "Canal", "Vendedor"],
            "Share": [top_category_share, top_region_share, top_channel_share, top_vendor_share],
        }
    )
    fig = px.bar(dep, x="Dimensão", y="Share", text_auto=".1f")
    fig.update_traces(hovertemplate="%{x}<br>Share: %{y:.1f}%<extra></extra>")
    fig.update_layout(height=300, showlegend=False)
    fig.update_yaxes(title_text="Share (%)")
    clean_figure(fig)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


with tabs[12]:
    section_header(
        "Evolução Recomendada do Projeto PHOS Fit",
        "Roadmap em fases para transformar o dashboard em plataforma analítica.",
    )
    st.markdown(
        """
        <div class="callout">
            <div class="callout-title">Fase 1 - Operacional</div>
            <div>Receita, custos, lucro, produtos, vendedores e leitura tática diária.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="callout" style="margin-top: 0.75rem;">
            <div class="callout-title">Fase 2 - Estratégica</div>
            <div>Margens, tendências, curva ABC, performance regional, desconto e segmentacao comercial.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="callout" style="margin-top: 0.75rem;">
            <div class="callout-title">Fase 3 - Inteligência Financeira</div>
            <div>Modelos preditivos, simulações financeiras, automatização de KPIs e apoio à decisão com IA.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Próximos incrementos práticos")
    st.write(
        [
            "Adicionar ID de cliente para LTV, frequência de compra e churn.",
            "Adicionar estoque para previsão de ruptura e giro por item.",
            "Adicionar custos logísticos detalhados para margem operacional mais precisa.",
            "Incluir metas para comparar realizado versus objetivo em cada aba.",
            "Publicar no Streamlit Cloud com revisão contínua do arquivo requirements.txt.",
        ]
    )



