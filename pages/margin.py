import streamlit as st


def render(
    monthly,
    current_total,
    previous_total,
    cat,
    vendedor,
    produto,
    current_df,
    top_profit_product,
):
    st.markdown("## Margem e Lucratividade")
    st.write("Página margin modularizada.")