import streamlit as st


def render(
    current_df,
    current_total,
    previous_total,
    regiao,
    canal,
    monthly,
):
    st.markdown("## Custos e Eficiência Operacional")
    st.write("Página costs modularizada.")