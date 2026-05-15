import streamlit as st


def render(
    current_df,
    current_total,
    previous_total,
    cat,
    canal,
    vendedor,
):
    st.markdown("## Preço e Desconto")
    st.write("Página pricing modularizada.")