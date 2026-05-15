import numpy as np
import pandas as pd


def grouped_sales(df: pd.DataFrame, dimension: str) -> pd.DataFrame:

    out = (
        df.groupby(dimension, as_index=False)
        .agg(
            Receita=("Receita", "sum"),
            Lucro=("Lucro", "sum"),
            Custo=("Custo", "sum"),
            Pedidos=("ID_Pedido", "nunique"),
            Quantidade=("Quantidade", "sum"),
            Desconto_Medio=("Desconto_Pct", "mean"),
            Frete_Medio=("Frete", "mean"),
        )
        .sort_values("Receita", ascending=False)
    )

    out["Margem"] = np.where(
        out["Receita"] != 0,
        out["Lucro"] / out["Receita"] * 100,
        0,
    )

    out["Lucro_Liquido"] = (
        out["Lucro"] - out["Frete_Medio"] * out["Pedidos"]
    )

    return out


def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:

    monthly = (
        df.groupby("Mes", as_index=False)
        .agg(
            Receita=("Receita", "sum"),
            Lucro=("Lucro", "sum"),
            Custo=("Custo", "sum"),
            Pedidos=("ID_Pedido", "nunique"),
            Quantidade=("Quantidade", "sum"),
            Frete=("Frete", "sum"),
            Desconto_Medio=("Desconto_Pct", "mean"),
        )
        .sort_values("Mes")
    )

    monthly["Data"] = monthly["Mes"].dt.to_timestamp()

    monthly["Margem"] = np.where(
        monthly["Receita"] != 0,
        monthly["Lucro"] / monthly["Receita"] * 100,
        0,
    )

    monthly["Lucro_Liquido"] = (
        monthly["Lucro"] - monthly["Frete"]
    )

    monthly["Acumulado_Receita"] = (
        monthly["Receita"].cumsum()
    )

    monthly["Acumulado_Lucro"] = (
        monthly["Lucro"].cumsum()
    )

    monthly["MoM_Receita"] = (
        monthly["Receita"].pct_change() * 100
    )

    monthly["MoM_Lucro"] = (
        monthly["Lucro"].pct_change() * 100
    )

    monthly["Ano"] = monthly["Data"].dt.year

    monthly["MesNumero"] = (
        monthly["Data"].dt.month
    )

    return monthly