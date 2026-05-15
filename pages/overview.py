import streamlit as st

from components.ui import render_kpis


def render(kpis):
    st.markdown("## Visão Geral")

    render_kpis(kpis)

    st.markdown("---")

    st.write("Página overview modularizada com sucesso.")