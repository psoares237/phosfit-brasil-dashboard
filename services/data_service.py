import numpy as np
import pandas as pd
import streamlit as st

from utils.formatters import MESES_PT


@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    data = pd.read_excel(file_path)
    data["Data"] = pd.to_datetime(data["Data"], errors="coerce")
    data = data.dropna(subset=["Data"]).copy()

    numeric_cols = [
        "Quantidade",
        "Preco_Unitario",
        "Desconto_Pct",
        "Valor_Total",
        "Custo_Total",
        "Lucro",
        "Frete",
    ]

    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)

    data["Mes"] = data["Data"].dt.to_period("M")
    data["Ano"] = data["Data"].dt.year
    data["MesNumero"] = data["Data"].dt.month
    data["MesNome"] = data["MesNumero"].map(MESES_PT)

    data["Receita"] = data["Valor_Total"]
    data["Custo"] = data["Custo_Total"]

    data["Margem"] = np.where(
        data["Receita"] != 0,
        data["Lucro"] / data["Receita"] * 100,
        0,
    )

    data["Desconto_Rate"] = np.where(
        data["Desconto_Pct"] > 1,
        data["Desconto_Pct"] / 100,
        data["Desconto_Pct"],
    )

    data["Desconto_Rate"] = data["Desconto_Rate"].clip(lower=0, upper=0.95)

    data["Preco_Bruto_Estimado"] = np.where(
        data["Desconto_Rate"] < 1,
        data["Receita"] / (1 - data["Desconto_Rate"]),
        data["Receita"],
    )

    data["Desconto_Valor_Estimado"] = (
        data["Preco_Bruto_Estimado"] - data["Receita"]
    ).clip(lower=0)

    data["Lucro_Liquido_Estimado"] = data["Lucro"] - data["Frete"]

    data["Margem_Liquida_Estimada"] = np.where(
        data["Receita"] != 0,
        data["Lucro_Liquido_Estimado"] / data["Receita"] * 100,
        0,
    )

    return data