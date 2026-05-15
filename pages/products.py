import streamlit as st


def render(
    produtos_full,
    top_revenue_product,
    top_profit_product,
    top_margin_product,
    worst_margin_product,
):
    st.markdown("## Análise de Produtos")
    st.write("Página products modularizada.")