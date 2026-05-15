import streamlit as st


def render(
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
):
    st.markdown("## Análise Comercial")
    st.write("Página commercial modularizada.")