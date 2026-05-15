import plotly.graph_objects as go


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