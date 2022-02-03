import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def plot_realms(realms,scores):
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=realms, 
        y=scores,
        opacity=.6,
        showlegend=False,
        marker_color = 'gold'
        ),
        )
    fig.update_yaxes(title_text="Score")
    fig.update_xaxes(title_text="Realms")

    fig.update_layout(
        height=400, width=600,
        font=dict(size=15)
    )

    return fig

def plot_elements(elementsPHY,scoresPHY,elementsMAG,scoresMAG):

    fig = make_subplots(rows=2, cols=1, vertical_spacing=0.15)

    fig.append_trace(go.Bar(
        x=elementsPHY, 
        y=scoresPHY,
        opacity=.6,
        showlegend=False,
        marker_color = 'tomato'
        ),
        row=1,
        col=1
    )

    fig.append_trace(go.Bar(
        x=elementsMAG, 
        y=scoresMAG,
        opacity=.6,
        showlegend=False,
        marker_color = 'lawngreen'
        ),
        row=2,
        col=1
    )

    fig.update_yaxes(title_text="Score PHY", row=1, col=1)
    fig.update_yaxes(title_text="Score MAG", row=2, col=1)
    fig.update_xaxes(title_text="Elements", row=2, col=1)
    
    fig.update_layout(
        height=800, width=600,
        font=dict(size=15)
    )

    return fig