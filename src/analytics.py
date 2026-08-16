"""
analytics.py
Real-time analytics engine for parking dashboard.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random


# ── Shared Plotly theme (nude + dark) ────────────────
NUDE_DARK = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(18,18,24,0.95)",
    font=dict(
        family="Inter, sans-serif",
        color="#c9b99a",
        size=12,
    ),
)

# Nude + dark color palette
NUDE_COLORS = [
    "#d4a76a", "#c9866b", "#a87e6f",
    "#8b6f6f", "#6b8b8b", "#7a9e9f",
    "#b8a99a", "#d4c5b0", "#e8d5b7",
    "#f0e0c8",
]


def create_occupancy_gauge(occupied, total):
    """
    Elite gauge chart for occupancy rate.
    """
    rate = round(occupied / max(total, 1) * 100, 1)
    color = (
        "#c9866b" if rate >= 80 else
        "#d4a76a" if rate >= 50 else
        "#7a9e9f"
    )

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=rate,
        title={"text": "Occupancy Rate",
               "font": {"size": 14,
                        "color": "#c9b99a"}},
        number={"suffix": "%",
                "font": {"size": 32,
                         "color": color,
                         "family": "Inter"}},
        delta={"reference": 70,
               "increasing": {"color": "#c9866b"},
               "decreasing": {"color": "#7a9e9f"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickcolor": "#4a4a5a",
                "tickwidth": 1,
            },
            "bar":  {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(18,18,24,0.8)",
            "bordercolor": "#2a2a3a",
            "steps": [
                {"range": [0, 50],
                 "color": "rgba(122,158,159,0.1)"},
                {"range": [50, 80],
                 "color": "rgba(212,167,106,0.1)"},
                {"range": [80, 100],
                 "color": "rgba(201,134,107,0.15)"},
            ],
            "threshold": {
                "line": {"color": "#e8d5b7",
                         "width": 2},
                "thickness": 0.75,
                "value": 90,
            },
        },
    ))
    fig.update_layout(
        **NUDE_DARK, height=240,
        margin=dict(t=40, b=10, l=20, r=20),
    )
    return fig


def create_floor_bar_chart(floor_stats):
    """
    Horizontal bar chart for floor-wise occupancy.
    """
    floors = list(floor_stats.keys())
    occ    = [floor_stats[f]["occupied"]  for f in floors]
    avail  = [floor_stats[f]["available"] for f in floors]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Occupied",
        y=floors, x=occ,
        orientation="h",
        marker=dict(
            color="#c9866b",
            line=dict(color="#1a1a24", width=1)
        ),
        text=occ,
        textposition="inside",
        textfont=dict(color="white", size=11),
    ))
    fig.add_trace(go.Bar(
        name="Available",
        y=floors, x=avail,
        orientation="h",
        marker=dict(
            color="#7a9e9f",
            line=dict(color="#1a1a24", width=1)
        ),
        text=avail,
        textposition="inside",
        textfont=dict(color="white", size=11),
    ))
    fig.update_layout(
        **NUDE_DARK,
        barmode="stack",
        height=220,
        title=dict(
            text="Floor-wise Status",
            font=dict(color="#c9b99a", size=13)
        ),
        legend=dict(
            orientation="h", y=1.1,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9b99a"),
        ),
        xaxis=dict(
            gridcolor="#2a2a3a",
            color="#6a6a7a",
            title="Slots",
        ),
        yaxis=dict(color="#c9b99a"),
        margin=dict(t=50, b=20, l=10, r=20),
    )
    return fig


def create_slot_heatmap(matrix, floors,
                        slots_per_floor):
    """
    Heatmap showing slot occupancy layout.
    Green = Available, Red = Occupied.
    """
    floor_labels = [
        f"Floor {i+1}" for i in range(floors)
    ]
    slot_labels  = [
        f"S{i+1:02d}" for i in range(slots_per_floor)
    ]

    # Custom colorscale: nude tones
    colorscale = [
        [0.0, "#1a2a1a"],   # empty/invalid
        [0.4, "#2a4a2a"],   # available (dark green)
        [0.5, "#7a9e9f"],   # available
        [0.6, "#d4a76a"],   # transitioning
        [1.0, "#c9866b"],   # occupied
    ]

    hover = []
    for i, floor in enumerate(floor_labels):
        row = []
        for j, slot in enumerate(slot_labels):
            val = matrix[i][j] if (
                i < len(matrix) and
                j < len(matrix[i])
            ) else -1
            status = "Occupied" if val == 1 \
                     else "Available" if val == 0 \
                     else "N/A"
            row.append(
                f"{floor} - {slot}<br>"
                f"Status: {status}"
            )
        hover.append(row)

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=slot_labels,
        y=floor_labels,
        colorscale=colorscale,
        showscale=False,
        hoverinfo="text",
        text=hover,
        xgap=3, ygap=3,
    ))

    # Add slot number annotations
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            val    = matrix[i][j]
            symbol = "🚗" if val == 1 else "✅"
            fig.add_annotation(
                x=slot_labels[j],
                y=floor_labels[i],
                text=symbol,
                showarrow=False,
                font=dict(size=10),
            )

    fig.update_layout(
        **NUDE_DARK,
        title=dict(
            text="🅿️ Live Parking Slot Map",
            font=dict(color="#c9b99a", size=14)
        ),
        height=280,
        margin=dict(t=50, b=20, l=80, r=20),
        xaxis=dict(
            side="top",
            color="#c9b99a",
        ),
        yaxis=dict(color="#c9b99a"),
    )
    return fig


def create_revenue_chart(hourly_traffic):
    """
    Area chart for hourly revenue/traffic.
    """
    hours = [f"{h:02d}:00" for h in range(24)]
    traffic = hourly_traffic

    # Generate revenue from traffic
    revenue = [
        t * random.uniform(40, 80)
        for t in traffic
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=revenue,
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(212,167,106,0.15)",
        line=dict(color="#d4a76a", width=2.5),
        name="Revenue",
    ))
    fig.add_trace(go.Scatter(
        x=hours,
        y=[t * 10 for t in traffic],
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(122,158,159,0.1)",
        line=dict(color="#7a9e9f",
                  width=1.5, dash="dot"),
        name="Traffic × 10",
    ))
    fig.update_layout(
        **NUDE_DARK,
        title=dict(
            text="📈 Hourly Revenue & Traffic",
            font=dict(color="#c9b99a", size=13)
        ),
        height=260,
        xaxis=dict(
            gridcolor="#2a2a3a",
            color="#6a6a7a",
            tickangle=-45,
        ),
        yaxis=dict(
            gridcolor="#2a2a3a",
            color="#6a6a7a",
            title="₹ Revenue",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9b99a"),
            orientation="h", y=1.1,
        ),
        margin=dict(t=50, b=50, l=20, r=20),
    )
    return fig


def create_vehicle_type_pie(type_counts):
    """
    Donut chart for vehicle type breakdown.
    """
    if not type_counts:
        type_counts = {"No Data": 1}

    fig = go.Figure(go.Pie(
        labels=list(type_counts.keys()),
        values=list(type_counts.values()),
        hole=0.6,
        marker=dict(
            colors=NUDE_COLORS[:len(type_counts)],
            line=dict(color="#1a1a24", width=2)
        ),
        textinfo="label+percent",
        textfont=dict(
            size=11, color="#c9b99a"
        ),
    ))
    fig.add_annotation(
        text=f"<b>{sum(type_counts.values())}</b>"
             "<br>Vehicles",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color="#d4a76a"),
    )
    fig.update_layout(
        **NUDE_DARK,
        title=dict(
            text="🚗 Vehicle Type Mix",
            font=dict(color="#c9b99a", size=13)
        ),
        height=280,
        showlegend=False,
        margin=dict(t=50, b=10, l=10, r=10),
    )
    return fig


def create_weekly_trend():
    """
    Bar chart for simulated weekly trend.
    """
    days    = ["Mon","Tue","Wed",
               "Thu","Fri","Sat","Sun"]
    traffic = [
        random.randint(80, 150),
        random.randint(90, 160),
        random.randint(85, 145),
        random.randint(95, 170),
        random.randint(120, 200),
        random.randint(150, 220),
        random.randint(60,  110),
    ]
    revenue = [t * random.uniform(45, 65)
               for t in traffic]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=days, y=revenue,
        name="Revenue (₹)",
        marker=dict(
            color=NUDE_COLORS[:7],
            line=dict(color="#1a1a24", width=1)
        ),
        text=[f"₹{r:.0f}" for r in revenue],
        textposition="outside",
        textfont=dict(
            size=10, color="#c9b99a"
        ),
    ))
    fig.update_layout(
        **NUDE_DARK,
        title=dict(
            text="📅 Weekly Revenue Trend",
            font=dict(color="#c9b99a", size=13)
        ),
        height=280,
        xaxis=dict(
            gridcolor="#2a2a3a",
            color="#c9b99a",
        ),
        yaxis=dict(
            gridcolor="#2a2a3a",
            color="#6a6a7a",
            title="Revenue (₹)",
        ),
        showlegend=False,
        margin=dict(t=50, b=20, l=20, r=20),
    )
    return fig


def create_sensor_health_chart(sensors):
    """
    Scatter plot for sensor health status.
    """
    if not sensors:
        return go.Figure()

    ids      = [s["sensor_id"] for s in sensors]
    readings = [s["readings"]  for s in sensors]
    errors   = [s["errors"]    for s in sensors]
    health   = [
        "#7a9e9f" if s["health"] == "OK"
        else "#c9866b"
        for s in sensors
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=ids, y=readings,
        name="Readings",
        marker_color="#d4a76a",
        opacity=0.8,
    ))
    fig.add_trace(go.Scatter(
        x=ids, y=errors,
        name="Errors",
        mode="markers+lines",
        marker=dict(
            color="#c9866b", size=8,
            symbol="x"
        ),
        line=dict(
            color="#c9866b", width=1,
            dash="dot"
        ),
        yaxis="y2",
    ))
    fig.update_layout(
        **NUDE_DARK,
        title=dict(
            text="📡 Sensor Health Monitor",
            font=dict(color="#c9b99a", size=13)
        ),
        height=280,
        xaxis=dict(
            color="#c9b99a",
            tickangle=-45,
            gridcolor="#2a2a3a",
        ),
        yaxis=dict(
            title="Readings",
            gridcolor="#2a2a3a",
            color="#6a6a7a",
        ),
        yaxis2=dict(
            title="Errors",
            overlaying="y",
            side="right",
            color="#c9866b",
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c9b99a"),
        ),
        margin=dict(t=50, b=60, l=20, r=50),
    )
    return fig