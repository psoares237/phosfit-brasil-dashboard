from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(
    page_title="PHOSFit Brasil Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊",
)


st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg: #0a0a0f;
            --panel: #151520;
            --panel-2: #1b1b28;
            --text: #f4f7fb;
            --muted: #95a2b8;
            --border: rgba(255,255,255,0.08);
            --green: #2dd4bf;
            --blue: #60a5fa;
            --violet: #a78bfa;
            --orange: #fb923c;
            --red: #f87171;
        }

        html, body, [class*="css"]  {
            font-family: 'Inter', system-ui, sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(96,165,250,0.14), transparent 30%),
                radial-gradient(circle at top right, rgba(167,139,250,0.12), transparent 25%),
                linear-gradient(180deg, #0a0a0f 0%, #10111a 100%);
            color: var(--text);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(26,26,38,0.96), rgba(16,17,26,0.98));
            border-right: 1px solid var(--border);
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        .hero {
            padding: 1.4rem 1.5rem;
            border: 1px solid var(--border);
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(26,26,38,0.94), rgba(15,15,23,0.96));
            box-shadow: 0 20px 50px rgba(0,0,0,0.25);
            margin-bottom: 1rem;
        }

        .hero h1 {
            margin: 0;
            font-size: 2.1rem;
            letter-spacing: -0.03em;
            color: var(--text);
        }

        .hero p {
            margin: 0.45rem 0 0;
            color: var(--muted);
            font-size: 0.98rem;
            line-height: 1.55;
        }

        .metric-card {
            background: linear-gradient(180deg, rgba(27,27,40,0.98), rgba(18,18,28,0.98));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1rem 0.9rem;
            box-shadow: 0 14px 34px rgba(0,0,0,0.18);
            min-height: 112px;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(96,165,250,0.25);
            box-shadow: 0 18px 38px rgba(0,0,0,0.24);
        }

        .metric-title {
            color: var(--muted);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            color: var(--text);
            font-size: 1.42rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.15;
        }

        .metric-delta {
            margin-top: 0.5rem;
            font-size: 0.92rem;
            font-weight: 600;
        }

        .metric-delta.up { color: var(--green); }
        .metric-delta.down { color: var(--red); }
        .metric-delta.flat { color: var(--muted); }

        .chart-card {
            background: linear-gradient(180deg, rgba(27,27,40,0.96), rgba(18,18,28,0.98));
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 1rem 1rem 0.5rem;
            box-shadow: 0 16px 34px rgba(0,0,0,0.16);
            height: 100%;
        }

        .chart-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 0.2rem;
        }

        .chart-subtitle {
            color: var(--muted);
            font-size: 0.88rem;
            margin-bottom: 0.75rem;
            line-height: 1.45;
        }

        footer-note {
            color: var(--muted);
        }

        .stDataFrame {
            border: 1px solid var(--border);
            border-radius: 14px;
            overflow: hidden;
        }

        .stSelectbox label, .stRadio label, .stMultiSelect label {
            color: var(--text) !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    data = pd.read_excel(file_path)
    data["Data"] = pd.to_datetime(data["Data"], errors="coerce")
    data = data.dropna(subset=["Data"]).copy()
    data["Mes"] = data["Data"].dt.to_period("M")
    data["Receita"] = pd.to_numeric(data["Valor_Total"], errors="coerce").fillna(0)
    data["Custo"] = pd.to_numeric(data["Custo_Total"], errors="coerce").fillna(0)
    data["Lucro"] = pd.to_numeric(data["Lucro"], errors="coerce").fillna(0)
    data["Quantidade"] = pd.to_numeric(data["Quantidade"], errors="coerce").fillna(0)
    data["Margem"] = data.apply(
        lambda row: (row["Lucro"] / row["Receita"]) if row["Receita"] else 0, axis=1
    )
    return data


def fmt_currency(value: float) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_int(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", ".")


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%".replace(".", ",")


def pct_change(current: float, previous: float) -> float | None:
    if previous in (0, None) or pd.isna(previous):
        return None
    return ((current - previous) / abs(previous)) * 100


def metric_card(title: str, value: str, delta: float | None, delta_label: str) -> None:
    if delta is None:
        delta_html = '<div class="metric-delta flat">Sem base comparável</div>'
    else:
        arrow = "▲" if delta >= 0 else "▼"
        cls = "up" if delta >= 0 else "down"
        delta_html = (
            f'<div class="metric-delta {cls}">{arrow} {fmt_pct(abs(delta))} '
            f"vs. {delta_label}</div>"
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


def chart_card(title: str, subtitle: str, figure: go.Figure) -> None:
    st.markdown(
        f"""
        <div class="chart-card">
            <div class="chart-title">{title}</div>
            <div class="chart-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


def clean_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#f4f7fb"),
        margin=dict(l=10, r=10, t=45, b=10),
        legend=dict(font=dict(color="#dbe4f0")),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.12)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.07)", zerolinecolor="rgba(255,255,255,0.12)")
    return fig


st.title("PHOSFit Brasil - Dashboard Executivo")
st.markdown(
    """
    <div class="hero">
        <h1>Dashboard TechStore</h1>
        <p>
            Análise executiva da base de vendas com KPIs, evolução mensal, mix de canais,
            performance por categoria, região, vendedores e formas de pagamento.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

data = load_data("base_vendas_esportes_original.xlsx")

if data.empty:
    st.error("Não foi possível carregar dados válidos da base.")
    st.stop()

meses = sorted(data["Mes"].dropna().unique())
opcao_periodo = st.sidebar.selectbox("Período", ["6 meses", "12 meses", "Tudo"], index=1)

if opcao_periodo == "6 meses":
    current_months = meses[-6:]
    comparison_months = meses[-12:-6] if len(meses) >= 12 else []
    periodo_label = "6 meses"
elif opcao_periodo == "12 meses":
    current_months = meses[-12:]
    comparison_months = meses[-24:-12] if len(meses) >= 24 else []
    periodo_label = "12 meses"
else:
    current_months = meses
    comparison_months = meses[-24:-12] if len(meses) >= 24 else []
    periodo_label = "histórico completo"

current_df = data[data["Mes"].isin(current_months)].copy()
previous_df = data[data["Mes"].isin(comparison_months)].copy()

if current_df.empty:
    st.warning("O filtro selecionado não retornou dados.")
    st.stop()

start_label = current_df["Data"].min().strftime("%d/%m/%Y")
end_label = current_df["Data"].max().strftime("%d/%m/%Y")

st.caption(f"Período exibido: {start_label} a {end_label} | comparação: período anterior equivalente")

receita_total = current_df["Receita"].sum()
lucro_total = current_df["Lucro"].sum()
custo_total = current_df["Custo"].sum()
pedidos_total = current_df["ID_Pedido"].nunique()
ticket_medio = receita_total / pedidos_total if pedidos_total else 0
margem_lucro = (lucro_total / receita_total * 100) if receita_total else 0

receita_prev = previous_df["Receita"].sum()
lucro_prev = previous_df["Lucro"].sum()
pedidos_prev = previous_df["ID_Pedido"].nunique()
ticket_prev = receita_prev / pedidos_prev if pedidos_prev else 0
margem_prev = (lucro_prev / receita_prev * 100) if receita_prev else 0

top_kpis = st.columns(5)
with top_kpis[0]:
    metric_card("Receita Total", fmt_currency(receita_total), pct_change(receita_total, receita_prev), "período anterior")
with top_kpis[1]:
    metric_card("Lucro Total", fmt_currency(lucro_total), pct_change(lucro_total, lucro_prev), "período anterior")
with top_kpis[2]:
    metric_card("Margem de Lucro", fmt_pct(margem_lucro), pct_change(margem_lucro, margem_prev), "período anterior")
with top_kpis[3]:
    metric_card("Ticket Médio", fmt_currency(ticket_medio), pct_change(ticket_medio, ticket_prev), "período anterior")
with top_kpis[4]:
    metric_card("Total de Pedidos", fmt_int(pedidos_total), pct_change(pedidos_total, pedidos_prev), "período anterior")

monthly = (
    current_df.groupby("Mes", as_index=False)
    .agg(
        Receita=("Receita", "sum"),
        Custo=("Custo", "sum"),
        Lucro=("Lucro", "sum"),
        Pedidos=("ID_Pedido", "nunique"),
        Quantidade=("Quantidade", "sum"),
    )
    .sort_values("Mes")
)
monthly["Margem"] = monthly.apply(lambda row: (row["Lucro"] / row["Receita"] * 100) if row["Receita"] else 0, axis=1)
monthly["Data"] = monthly["Mes"].dt.to_timestamp()

col1, col2 = st.columns(2)
with col1:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=monthly["Data"],
            y=monthly["Receita"],
            mode="lines+markers",
            name="Receita",
            line=dict(color="#60a5fa", width=3),
            hovertemplate="%{x|%b/%Y}<br>Receita: %{y:,.2f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=monthly["Data"],
            y=monthly["Lucro"],
            mode="lines+markers",
            name="Lucro",
            line=dict(color="#2dd4bf", width=3),
            hovertemplate="%{x|%b/%Y}<br>Lucro: %{y:,.2f}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title=None,
        height=420,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="left", x=0),
    )
    fig.update_yaxes(title_text="Receita", secondary_y=False, tickprefix="R$ ")
    fig.update_yaxes(title_text="Lucro", secondary_y=True, tickprefix="R$ ")
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Evolução mensal de Receita vs Lucro</div>'
        '<div class="chart-subtitle">Mostra o ritmo da operação e o comportamento do resultado ao longo do tempo.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    cat = (
        current_df.groupby("Categoria", as_index=False)["Receita"].sum().sort_values("Receita", ascending=True)
    )
    fig = px.bar(
        cat,
        x="Receita",
        y="Categoria",
        orientation="h",
        color="Receita",
        color_continuous_scale=["#1d4ed8", "#60a5fa", "#a78bfa"],
        text_auto=".2s",
    )
    fig.update_traces(
        hovertemplate="Categoria: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>",
        textposition="outside",
    )
    fig.update_layout(height=420, coloraxis_showscale=False)
    fig.update_xaxes(tickprefix="R$ ")
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Receita por Categoria</div>'
        '<div class="chart-subtitle">Identifica onde está a maior concentração de faturamento.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

col3, col4 = st.columns(2)
with col3:
    canal = current_df.groupby("Canal_Venda", as_index=False)["Receita"].sum().sort_values("Receita", ascending=True)
    fig = px.bar(
        canal,
        x="Receita",
        y="Canal_Venda",
        orientation="h",
        color="Canal_Venda",
        color_discrete_sequence=["#60a5fa", "#a78bfa", "#2dd4bf", "#fb923c", "#f87171"],
        text_auto=".2s",
    )
    fig.update_traces(
        hovertemplate="Canal: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>",
        textposition="outside",
        showlegend=False,
    )
    fig.update_layout(height=380)
    fig.update_xaxes(tickprefix="R$ ")
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Receita por Canal de Venda</div>'
        '<div class="chart-subtitle">Compara o peso de cada canal na geração de receita.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    regiao = current_df.groupby("Regiao", as_index=False)["Receita"].sum().sort_values("Receita", ascending=True)
    fig = px.bar(
        regiao,
        x="Receita",
        y="Regiao",
        orientation="h",
        color="Regiao",
        color_discrete_sequence=["#1d4ed8", "#60a5fa", "#2dd4bf", "#a78bfa", "#fb923c"],
        text_auto=".2s",
    )
    fig.update_traces(
        hovertemplate="Região: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>",
        textposition="outside",
        showlegend=False,
    )
    fig.update_layout(height=380)
    fig.update_xaxes(tickprefix="R$ ")
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Receita por Região</div>'
        '<div class="chart-subtitle">Mostra a distribuição geográfica das vendas.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)
with col5:
    produtos = (
        current_df.groupby("Produto", as_index=False)["Quantidade"]
        .sum()
        .sort_values("Quantidade", ascending=False)
        .head(10)
        .sort_values("Quantidade", ascending=True)
    )
    fig = px.bar(
        produtos,
        x="Quantidade",
        y="Produto",
        orientation="h",
        color="Quantidade",
        color_continuous_scale=["#0f766e", "#2dd4bf", "#99f6e4"],
        text_auto=".2s",
    )
    fig.update_traces(
        hovertemplate="Produto: %{y}<br>Quantidade: %{x:,.0f}<extra></extra>",
        textposition="outside",
    )
    fig.update_layout(height=420, coloraxis_showscale=False)
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Top 10 Produtos mais vendidos</div>'
        '<div class="chart-subtitle">Ranking por volume, útil para entender giro de estoque e demanda.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    margem = monthly.copy()
    fig = px.area(
        margem,
        x="Data",
        y="Margem",
        color_discrete_sequence=["#a78bfa"],
        line_shape="spline",
    )
    fig.update_traces(
        hovertemplate="%{x|%b/%Y}<br>Margem: %{y:.1f}%<extra></extra>",
        fillcolor="rgba(167,139,250,0.22)",
        line=dict(color="#a78bfa", width=3),
    )
    fig.update_layout(height=420, showlegend=False)
    fig.update_yaxes(title_text="Margem (%)")
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Evolução da Margem de Lucro</div>'
        '<div class="chart-subtitle">Ajuda a ver se a rentabilidade melhora ou perde força ao longo dos meses.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

col7, col8 = st.columns(2)
with col7:
    pagamento = current_df.groupby("Forma_Pagamento", as_index=False)["Receita"].sum().sort_values("Receita", ascending=False)
    fig = px.pie(
        pagamento,
        names="Forma_Pagamento",
        values="Receita",
        hole=0.52,
        color_discrete_sequence=["#60a5fa", "#2dd4bf", "#a78bfa", "#fb923c", "#f87171"],
    )
    fig.update_traces(
        textinfo="percent+label",
        hovertemplate="%{label}<br>Receita: R$ %{value:,.2f}<extra></extra>",
    )
    fig.update_layout(height=380, legend_title_text="")
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Comparativo por Forma de Pagamento</div>'
        '<div class="chart-subtitle">Mostra quais meios de pagamento concentram mais faturamento.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

with col8:
    vendedores = (
        current_df.groupby("Vendedor", as_index=False)["Receita"]
        .sum()
        .sort_values("Receita", ascending=False)
        .head(5)
        .sort_values("Receita", ascending=True)
    )
    fig = px.bar(
        vendedores,
        x="Receita",
        y="Vendedor",
        orientation="h",
        color="Receita",
        color_continuous_scale=["#1d4ed8", "#60a5fa", "#a78bfa"],
        text_auto=".2s",
    )
    fig.update_traces(
        hovertemplate="Vendedor: %{y}<br>Receita: R$ %{x:,.2f}<extra></extra>",
        textposition="outside",
    )
    fig.update_layout(height=380, coloraxis_showscale=False)
    fig.update_xaxes(tickprefix="R$ ")
    clean_figure(fig)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="chart-title">Ranking dos 5 Vendedores</div>'
        '<div class="chart-subtitle">Lista os vendedores com maior geração de receita no período.</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("## Resumo mensal detalhado")

table = monthly.copy()
table["Mes"] = table["Mes"].astype(str)
table["Receita"] = table["Receita"].map(fmt_currency)
table["Custo"] = table["Custo"].map(fmt_currency)
table["Lucro"] = table["Lucro"].map(fmt_currency)
table["Margem"] = table["Margem"].map(fmt_pct)
table["Pedidos"] = table["Pedidos"].map(fmt_int)
table["Quantidade"] = table["Quantidade"].map(fmt_int)

st.dataframe(
    table.rename(
        columns={
            "Mes": "Mês",
            "Receita": "Receita",
            "Custo": "Custo",
            "Lucro": "Lucro",
            "Margem": "Margem",
            "Pedidos": "Pedidos",
            "Quantidade": "Unidades",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    f"Dados reais da base carregada em {datetime.now().strftime('%d/%m/%Y')}. "
    "Os gráficos e KPIs são calculados diretamente da planilha."
)
