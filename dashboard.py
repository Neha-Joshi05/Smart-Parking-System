"""
dashboard.py — Smart Parking System Elite Dashboard
Nude + Dark tone | Interactive | Real-time
Run: python -m streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
import random
import sys
from datetime import datetime

sys.path.insert(0, ".")
from simulation.parking_simulator import ParkingLot
from simulation.sensor            import SensorArray
from src.parking_manager          import ParkingManager
from src.analytics                import (
    create_occupancy_gauge,
    create_floor_bar_chart,
    create_slot_heatmap,
    create_revenue_chart,
    create_vehicle_type_pie,
    create_weekly_trend,
    create_sensor_health_chart,
    NUDE_COLORS,
)
from src.alerts import AlertSystem

# ── Page config ───────────────────────────────────────
st.set_page_config(
    page_title="Smart Parking System",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Elite Nude + Dark CSS ─────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');
  * { font-family:'Inter',sans-serif !important; }

  /* ── Base ── */
  .stApp {
    background: linear-gradient(
      135deg, #0d0d12 0%, #12121a 50%, #0f0f16 100%
    );
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: linear-gradient(
      180deg, #0d0d12, #12121a
    ) !important;
    border-right: 1px solid #2a2a3a;
  }

  /* ── Metrics ── */
  [data-testid="stMetric"] {
    background: linear-gradient(
      135deg, #1a1a24, #1e1e2a
    );
    border: 1px solid #2a2a3a;
    border-radius: 16px;
    padding: 20px !important;
    position: relative;
    overflow: hidden;
  }
  [data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(
      90deg, #d4a76a, #c9866b, #a87e6f
    );
  }
  [data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 900 !important;
    background: linear-gradient(
      135deg, #d4a76a, #c9866b
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  [data-testid="stMetricLabel"] {
    color: #8a7a6a !important;
    font-size: 0.72rem !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
  }
  [data-testid="stMetricDelta"] {
    font-size: 0.78rem !important;
  }

  /* ── Hero Card ── */
  .hero-card {
    background: linear-gradient(
      135deg, #1a1a24, #1e1e2a, #1a1a24
    );
    border: 1px solid #2a2a3a;
    border-radius: 20px;
    padding: 28px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
  }
  .hero-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(
      90deg, #d4a76a, #c9866b, #7a9e9f, #d4a76a
    );
    background-size: 200% 100%;
    animation: shimmer 4s linear infinite;
  }
  .hero-card::after {
    content: '';
    position: absolute;
    bottom: -30px; right: -30px;
    width: 120px; height: 120px;
    background: radial-gradient(
      circle, rgba(212,167,106,0.08), transparent
    );
    border-radius: 50%;
  }
  @keyframes shimmer {
    0%   { background-position: 0% }
    100% { background-position: 200% }
  }

  /* ── Info Card ── */
  .info-card {
    background: #1a1a24;
    border: 1px solid #2a2a3a;
    border-radius: 14px;
    padding: 16px 20px;
    margin: 8px 0;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
  }
  .info-card:hover { border-color: #d4a76a; }

  /* ── Slot Cards ── */
  .slot-occupied {
    background: linear-gradient(
      135deg, #2a1a1a, #241a1a
    );
    border: 1px solid #c9866b;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    margin: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #c9866b;
  }
  .slot-available {
    background: linear-gradient(
      135deg, #1a2a1a, #1a241a
    );
    border: 1px solid #7a9e9f;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    margin: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #7a9e9f;
  }
  .slot-reserved {
    background: linear-gradient(
      135deg, #1a1a2a, #1a1a24
    );
    border: 1px solid #d4a76a;
    border-radius: 10px;
    padding: 10px;
    text-align: center;
    margin: 3px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #d4a76a;
  }

  /* ── Alert Cards ── */
  .alert-critical {
    background: rgba(201,134,107,0.12);
    border-left: 4px solid #c9866b;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px; margin: 6px 0;
    color: #e8c4b0; font-size: 0.875rem;
  }
  .alert-warning {
    background: rgba(212,167,106,0.12);
    border-left: 4px solid #d4a76a;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px; margin: 6px 0;
    color: #e8d5b7; font-size: 0.875rem;
  }
  .alert-info {
    background: rgba(122,158,159,0.12);
    border-left: 4px solid #7a9e9f;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px; margin: 6px 0;
    color: #b8d4d4; font-size: 0.875rem;
  }
  .alert-success {
    background: rgba(139,158,122,0.12);
    border-left: 4px solid #8b9e7a;
    border-radius: 0 10px 10px 0;
    padding: 12px 16px; margin: 6px 0;
    color: #c4d4b8; font-size: 0.875rem;
  }

  /* ── Section Title ── */
  .section-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #c9b99a;
    margin: 14px 0 8px;
    padding-left: 10px;
    border-left: 3px solid #d4a76a;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }

  /* ── Event Log ── */
  .event-entry {
    background: #1a1a24;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 5px 0;
    display: flex;
    align-items: center;
    gap: 10px;
    border: 1px solid #2a2a3a;
    font-size: 0.82rem;
  }
  .event-dot-entry { color: #7a9e9f; }
  .event-dot-exit  { color: #c9866b; }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(
      135deg, #d4a76a, #c9866b
    ) !important;
    color: #1a1a24 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
  }

  /* ── Dataframe ── */
  div[data-testid="stDataFrame"] {
    border: 1px solid #2a2a3a !important;
    border-radius: 12px !important;
  }

  /* ── Select / Input ── */
  .stSelectbox > div > div {
    background: #1a1a24 !important;
    border-color: #2a2a3a !important;
    color: #c9b99a !important;
  }

  /* ── Live Badge ── */
  .live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(122,158,159,0.15);
    border: 1px solid #7a9e9f;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #7a9e9f;
  }
  .live-dot {
    width: 6px; height: 6px;
    background: #7a9e9f;
    border-radius: 50%;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0.3; }
  }

  /* ── Progress Bar ── */
  .prog-bar-bg {
    background: #2a2a3a;
    border-radius: 4px;
    height: 8px;
    margin: 4px 0;
  }
  .prog-bar-fill {
    height: 8px;
    border-radius: 4px;
    background: linear-gradient(
      90deg, #d4a76a, #c9866b
    );
    transition: width 0.5s ease;
  }

  /* ── Tab styling ── */
  .stTabs [data-baseweb="tab-list"] {
    background: #1a1a24;
    border-radius: 10px;
    gap: 4px;
    padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    color: #8a7a6a !important;
    font-weight: 600;
    border-radius: 8px !important;
  }
  .stTabs [aria-selected="true"] {
    background: linear-gradient(
      135deg, #d4a76a, #c9866b
    ) !important;
    color: #1a1a24 !important;
  }
</style>
""", unsafe_allow_html=True)

# ── Initialize session state ──────────────────────────
if "parking_lot" not in st.session_state:
    st.session_state.parking_lot = ParkingLot(
        name="TechPark Smart Mall",
        floors=3,
        slots_per_floor=8,
    )
if "auto_mode" not in st.session_state:
    st.session_state.auto_mode = True
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()

lot     = st.session_state.parking_lot
manager = ParkingManager(lot)
alerts  = AlertSystem(lot)

# ── Auto simulate ─────────────────────────────────────
if st.session_state.auto_mode:
    lot.auto_simulate()

# ── Get live stats ────────────────────────────────────
stats       = lot.get_dashboard_stats()
active_alerts = alerts.check_all()
sensor_data = lot.sensor_array.read_all()
revenue_proj= manager.calculate_revenue_projection()
vtype_counts= manager.get_vehicle_type_breakdown()
duration_st = manager.get_duration_stats()
heatmap_mat = manager.get_slot_heatmap_data()
best_floor, best_avail = \
    manager.get_floor_recommendation()

# ═══════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════
st.sidebar.markdown("""
<div style='text-align:center;padding:20px 0 10px'>
  <div style='font-size:2.5rem'>🅿️</div>
  <div style='font-size:1.2rem;font-weight:900;
    background:linear-gradient(135deg,#d4a76a,#c9866b);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-top:6px'>
    SmartPark
  </div>
  <div style='color:#6a6a7a;font-size:0.75rem;
    margin-top:2px'>
    Ultrasonic Sensor System
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown(
    '<div class="live-badge">'
    '<div class="live-dot"></div>'
    'LIVE MONITORING</div>',
    unsafe_allow_html=True
)

st.sidebar.markdown("---")

# Quick Stats
st.sidebar.markdown(
    '<div class="section-title">📊 Quick Stats</div>',
    unsafe_allow_html=True
)
occ_rate = stats["occ_rate"]
col1, col2 = st.sidebar.columns(2)
col1.metric("🚗 Parked", stats["occupied"])
col2.metric("✅ Free",   stats["available"])
col1.metric("💰 Revenue",
            f"₹{stats['revenue']:.0f}")
col2.metric("🚘 Total",
            stats["total_vehicles"])

# Occupancy bar
st.sidebar.markdown(f"""
<div style='margin:10px 0'>
  <div style='display:flex;justify-content:space-between;
    font-size:0.78rem;color:#8a7a6a;margin-bottom:4px'>
    <span>Occupancy</span>
    <span style='color:#d4a76a'>{occ_rate}%</span>
  </div>
  <div class='prog-bar-bg'>
    <div class='prog-bar-fill'
      style='width:{occ_rate}%'></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Controls
st.sidebar.markdown(
    '<div class="section-title">⚙️ Controls</div>',
    unsafe_allow_html=True
)
st.session_state.auto_mode = st.sidebar.toggle(
    "🤖 Auto Simulation",
    value=st.session_state.auto_mode
)

if st.sidebar.button("🚗 Simulate Entry"):
    v, slot = lot.vehicle_entry()
    if v:
        st.sidebar.success(
            f"✅ {v.plate_number} → {slot}"
        )
    else:
        st.sidebar.error("❌ Parking Full!")

if st.sidebar.button("🔄 Simulate Exit"):
    v, fee = lot.vehicle_exit()
    if v:
        st.sidebar.success(
            f"✅ {v.plate_number} left | ₹{fee}"
        )

# Refresh
refresh_rate = st.sidebar.selectbox(
    "🔁 Refresh Rate",
    ["5s", "10s", "30s", "Manual"],
    index=1,
)
if refresh_rate != "Manual":
    interval = int(refresh_rate[:-1])
    time.sleep(0.1)
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    st.sidebar.caption(
        f"Auto-refresh: {refresh_rate}"
    )

st.sidebar.markdown("---")

# Floor recommendation
st.sidebar.markdown(f"""
<div class='info-card'>
  <div style='font-size:0.75rem;color:#8a7a6a;
    text-transform:uppercase;letter-spacing:1px;
    margin-bottom:6px'>
    🎯 Recommended
  </div>
  <div style='font-size:1rem;font-weight:700;
    color:#d4a76a'>
    {best_floor}
  </div>
  <div style='font-size:0.8rem;color:#8a7a6a'>
    {best_avail} slots available
  </div>
</div>
""", unsafe_allow_html=True)

# Alerts count
if active_alerts:
    st.sidebar.warning(
        f"🚨 {len(active_alerts)} Active Alert(s)"
    )

# ═══════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════

# Hero Header
now_str = datetime.now().strftime(
    "%d %b %Y | %H:%M:%S"
)
st.markdown(f"""
<div class='hero-card'>
  <div style='display:flex;align-items:center;
    justify-content:space-between;flex-wrap:wrap;gap:12px'>
    <div>
      <h1 style='margin:0;font-size:1.8rem;
        font-weight:900;
        background:linear-gradient(
          135deg,#d4a76a,#c9866b,#a87e6f
        );
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent'>
        🅿️ Smart Parking System
      </h1>
      <p style='color:#8a7a6a;margin:6px 0 0;
        font-size:0.9rem'>
        TechPark Smart Mall •
        Ultrasonic Sensor Network •
        Real-time Monitoring
      </p>
    </div>
    <div style='text-align:right'>
      <div class='live-badge'>
        <div class='live-dot'></div>
        LIVE
      </div>
      <div style='color:#6a6a7a;font-size:0.78rem;
        margin-top:6px'>
        {now_str}
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric(
    "🏢 Total Slots",  stats["total"],
    delta=None
)
c2.metric(
    "🚗 Occupied",     stats["occupied"],
    delta=f"{stats['occ_rate']}%"
)
c3.metric(
    "✅ Available",    stats["available"],
    delta=f"-{stats['occupied']}"
    if stats["available"] < stats["total"] // 2
    else None
)
c4.metric(
    "💰 Revenue",
    f"₹{stats['revenue']:.0f}",
    delta=f"₹{revenue_proj['daily']:.0f}/day est."
)
c5.metric(
    "🚘 Vehicles Today",
    stats["total_vehicles"],
)
c6.metric(
    "⏱️ Avg Duration",
    f"{duration_st['avg']:.0f}m",
    delta=f"Max {duration_st['max']:.0f}m"
)

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Live Map",
    "📊 Analytics",
    "🚗 Vehicles",
    "📡 Sensors",
    "⚙️ Management",
])

# ══════════════════════════════════════════════
# TAB 1 — LIVE MAP
# ══════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Slot heatmap
        fig_heat = create_slot_heatmap(
            heatmap_mat,
            lot.floors,
            lot.slots_per_floor,
        )
        st.plotly_chart(
            fig_heat, use_container_width=True
        )

        # Interactive slot grid
        st.markdown(
            '<div class="section-title">'
            '🅿️ Interactive Slot View</div>',
            unsafe_allow_html=True
        )

        # Floor filter
        floor_filter = st.selectbox(
            "Select Floor",
            ["All Floors"] + [
                f"Floor {i}"
                for i in range(1, lot.floors + 1)
            ],
        )

        # Render slots
        filtered_slots = [
            s for s in stats["slots"]
            if floor_filter == "All Floors" or
               s["floor"] == floor_filter
        ]

        cols_per_row = lot.slots_per_floor
        rows = [
            filtered_slots[i:i+cols_per_row]
            for i in range(
                0, len(filtered_slots), cols_per_row
            )
        ]

        for row_slots in rows:
            cols = st.columns(len(row_slots))
            for col, slot in zip(cols, row_slots):
                with col:
                    if slot["occupied"]:
                        st.markdown(f"""
                        <div class='slot-occupied'>
                          🚗<br>
                          <b>{slot['slot_id']}</b><br>
                          <small>{slot['vehicle'] or ''}</small>
                          <br>
                          <small>{slot['duration'] or ''}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    elif slot["reserved"]:
                        st.markdown(f"""
                        <div class='slot-reserved'>
                          🔒<br>
                          <b>{slot['slot_id']}</b><br>
                          <small>Reserved</small>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='slot-available'>
                          ✅<br>
                          <b>{slot['slot_id']}</b><br>
                          <small>Available</small>
                        </div>
                        """, unsafe_allow_html=True)

    with col_right:
        # Gauge
        fig_gauge = create_occupancy_gauge(
            stats["occupied"], stats["total"]
        )
        st.plotly_chart(
            fig_gauge, use_container_width=True
        )

        # Floor stats
        fig_floor = create_floor_bar_chart(
            stats["floor_stats"]
        )
        st.plotly_chart(
            fig_floor, use_container_width=True
        )

        # Alerts
        st.markdown(
            '<div class="section-title">'
            '🚨 Live Alerts</div>',
            unsafe_allow_html=True
        )
        if active_alerts:
            for alert in active_alerts:
                css_class = {
                    "CRITICAL": "alert-critical",
                    "WARNING":  "alert-warning",
                    "INFO":     "alert-info",
                    "SUCCESS":  "alert-success",
                }.get(alert["type"], "alert-info")
                st.markdown(f"""
                <div class='{css_class}'>
                  {alert['icon']}
                  {alert['message']}
                  <span style='color:#6a6a7a;
                    font-size:0.75rem;
                    float:right'>
                    {alert['time']}
                  </span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-success'>
              ✅ All systems normal!
              No alerts at this time.
            </div>
            """, unsafe_allow_html=True)

        # Entry/Exit log
        st.markdown(
            '<div class="section-title">'
            '📋 Recent Events</div>',
            unsafe_allow_html=True
        )
        for event in reversed(
            stats["entry_log"]
        ):
            dot_class = (
                "event-dot-entry"
                if event["event"] == "ENTRY"
                else "event-dot-exit"
            )
            icon = (
                "🟢" if event["event"] == "ENTRY"
                else "🔴"
            )
            fee_str = (
                f" | {event.get('fee','')}"
                if "fee" in event else ""
            )
            st.markdown(f"""
            <div class='event-entry'>
              <span>{icon}</span>
              <div>
                <span style='color:#c9b99a;
                  font-weight:600'>
                  {event['plate']}
                </span>
                <span style='color:#6a6a7a'>
                  → {event['slot']}
                  {fee_str}
                </span>
                <br>
                <span style='color:#6a6a7a;
                  font-size:0.75rem'>
                  {event['type']} •
                  {event['time']}
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2 — ANALYTICS
# ══════════════════════════════════════════════
with tab2:

    col1, col2 = st.columns(2)

    with col1:
        # Revenue chart
        fig_rev = create_revenue_chart(
            stats["hourly"]
        )
        st.plotly_chart(
            fig_rev, use_container_width=True
        )

        # Vehicle type pie
        fig_pie = create_vehicle_type_pie(
            vtype_counts
        )
        st.plotly_chart(
            fig_pie, use_container_width=True
        )

    with col2:
        # Weekly trend
        fig_week = create_weekly_trend()
        st.plotly_chart(
            fig_week, use_container_width=True
        )

        # Revenue projection
        st.markdown(
            '<div class="section-title">'
            '💰 Revenue Projection</div>',
            unsafe_allow_html=True
        )
        for label, value in [
            ("Today (Current)",
             f"₹{revenue_proj['current']:,.0f}"),
            ("Today (Projected)",
             f"₹{revenue_proj['daily']:,.0f}"),
            ("Monthly",
             f"₹{revenue_proj['monthly']:,.0f}"),
            ("Yearly",
             f"₹{revenue_proj['yearly']:,.0f}"),
        ]:
            st.markdown(f"""
            <div class='info-card'>
              <div style='display:flex;
                justify-content:space-between'>
                <span style='color:#8a7a6a;
                  font-size:0.85rem'>{label}</span>
                <span style='color:#d4a76a;
                  font-weight:700'>{value}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # Duration stats
    st.markdown("---")
    st.markdown(
        '<div class="section-title">'
        '⏱️ Parking Duration Stats</div>',
        unsafe_allow_html=True
    )
    d1, d2, d3 = st.columns(3)
    d1.metric(
        "⏱️ Avg Duration",
        f"{duration_st['avg']:.1f} min"
    )
    d2.metric(
        "⚡ Min Duration",
        f"{duration_st['min']:.1f} min"
    )
    d3.metric(
        "🕐 Max Duration",
        f"{duration_st['max']:.1f} min"
    )

# ══════════════════════════════════════════════
# TAB 3 — VEHICLES
# ══════════════════════════════════════════════
with tab3:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            '<div class="section-title">'
            '🚗 Currently Parked</div>',
            unsafe_allow_html=True
        )
        occupied_slots = [
            s for s in stats["slots"]
            if s["occupied"]
        ]
        if occupied_slots:
            df_occ = pd.DataFrame(occupied_slots)[
                ["slot_id", "floor", "type",
                 "vehicle", "entry_time",
                 "duration", "total_uses"]
            ]
            df_occ.columns = [
                "Slot", "Floor", "Type",
                "Vehicle", "Entry", "Duration",
                "Total Uses"
            ]
            st.dataframe(
                df_occ,
                use_container_width=True,
                height=350,
            )
        else:
            st.info("No vehicles currently parked!")

    with col2:
        st.markdown(
            '<div class="section-title">'
            '📜 Vehicle History</div>',
            unsafe_allow_html=True
        )
        if stats["history"]:
            df_hist = pd.DataFrame(
                stats["history"]
            )
            cols_to_show = [
                c for c in [
                    "plate_number", "vehicle_type",
                    "slot_id", "entry_time",
                    "exit_time", "duration",
                    "fee", "status"
                ] if c in df_hist.columns
            ]
            st.dataframe(
                df_hist[cols_to_show],
                use_container_width=True,
                height=350,
            )
        else:
            st.info(
                "No vehicle history yet!"
            )

# ══════════════════════════════════════════════
# TAB 4 — SENSORS
# ══════════════════════════════════════════════
with tab4:
    col1, col2 = st.columns([2, 1])

    with col1:
        # Sensor health chart
        fig_sensor = create_sensor_health_chart(
            sensor_data[:12]
        )
        st.plotly_chart(
            fig_sensor, use_container_width=True
        )

        # Sensor data table
        st.markdown(
            '<div class="section-title">'
            '📡 Sensor Readings</div>',
            unsafe_allow_html=True
        )
        df_sensors = pd.DataFrame(sensor_data)
        cols_show  = [
            "sensor_id", "slot_id", "location",
            "distance_cm", "occupied",
            "health", "readings", "errors"
        ]
        cols_show = [
            c for c in cols_show
            if c in df_sensors.columns
        ]
        st.dataframe(
            df_sensors[cols_show],
            use_container_width=True,
            height=300,
        )

    with col2:
        # Sensor stats
        total_s   = len(sensor_data)
        healthy   = sum(
            1 for s in sensor_data
            if s["health"] == "OK"
        )
        faulty    = total_s - healthy
        detecting = sum(
            1 for s in sensor_data
            if s["occupied"]
        )

        st.metric("📡 Total Sensors",    total_s)
        st.metric("✅ Healthy",           healthy)
        st.metric("❌ Faulty",            faulty)
        st.metric("🚗 Detecting Vehicle", detecting)

        st.markdown("---")

        # Sensor info
        st.markdown(
            '<div class="section-title">'
            '💡 HC-SR04 Specs</div>',
            unsafe_allow_html=True
        )
        for spec, val in [
            ("Range",    "2 — 400 cm"),
            ("Accuracy", "±3 mm"),
            ("Frequency","40 Hz"),
            ("Voltage",  "5V DC"),
            ("Beam Angle","15°"),
            ("Threshold","< 20 cm = Occupied"),
        ]:
            st.markdown(f"""
            <div class='info-card'
              style='padding:10px 14px'>
              <div style='display:flex;
                justify-content:space-between'>
                <span style='color:#8a7a6a;
                  font-size:0.8rem'>{spec}</span>
                <span style='color:#d4a76a;
                  font-size:0.8rem;
                  font-weight:600'>{val}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 5 — MANAGEMENT
# ══════════════════════════════════════════════
with tab5:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="section-title">'
            '🚗 Manual Vehicle Entry</div>',
            unsafe_allow_html=True
        )
        pref = st.selectbox(
            "Slot Preference",
            ["nearest", "premium",
             "ev", "handicap"]
        )
        if st.button("➕ Add Vehicle Entry"):
            v, slot = lot.vehicle_entry()
            if v:
                st.success(
                    f"✅ {v.vehicle_type} "
                    f"({v.plate_number}) "
                    f"→ Slot {slot}"
                )
            else:
                st.error("❌ Parking is FULL!")

        st.markdown("---")
        st.markdown(
            '<div class="section-title">'
            '🔄 Manual Vehicle Exit</div>',
            unsafe_allow_html=True
        )
        occ_ids = [
            s["slot_id"] for s in stats["slots"]
            if s["occupied"]
        ]
        if occ_ids:
            sel_slot = st.selectbox(
                "Select Slot to Exit", occ_ids
            )
            if st.button("🚗 Process Exit"):
                v, fee = lot.vehicle_exit(sel_slot)
                if v:
                    st.success(
                        f"✅ {v.plate_number} exited"
                        f" | Fee: ₹{fee}"
                    )
                    st.balloons()
        else:
            st.info("No vehicles to exit!")

    with col2:
        st.markdown(
            '<div class="section-title">'
            '🔒 Reserve a Slot</div>',
            unsafe_allow_html=True
        )
        avail_ids = [
            s["slot_id"] for s in stats["slots"]
            if not s["occupied"] and
               not s["reserved"]
        ]
        if avail_ids:
            res_slot = st.selectbox(
                "Select Slot to Reserve",
                avail_ids
            )
            res_name = st.text_input(
                "Reserved For",
                placeholder="Name or Vehicle Plate"
            )
            if st.button("🔒 Reserve Slot"):
                if res_name:
                    lot.slots[
                        res_slot
                    ].reserved = True
                    st.success(
                        f"✅ {res_slot} reserved"
                        f" for {res_name}!"
                    )
                else:
                    st.error(
                        "Please enter a name!"
                    )
        else:
            st.info("No slots available to reserve!")

        st.markdown("---")

        # System info
        st.markdown(
            '<div class="section-title">'
            '🖥️ System Info</div>',
            unsafe_allow_html=True
        )
        for label, val in [
            ("Lot Name",       lot.name),
            ("Total Floors",   lot.floors),
            ("Slots/Floor",    lot.slots_per_floor),
            ("Total Sensors",  len(sensor_data)),
            ("Active Since",   "Today 08:00 AM"),
            ("System Status",  "✅ Operational"),
        ]:
            st.markdown(f"""
            <div class='info-card'
              style='padding:10px 14px'>
              <div style='display:flex;
                justify-content:space-between'>
                <span style='color:#8a7a6a;
                  font-size:0.82rem'>{label}</span>
                <span style='color:#c9b99a;
                  font-size:0.82rem;
                  font-weight:600'>{val}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style='text-align:center;color:#4a4a5a;
  font-size:0.75rem;padding:10px 0'>
  🅿️ SmartPark Dashboard •
  Ultrasonic Sensor Network •
  Last updated: {now_str}
</div>
""", unsafe_allow_html=True)

# ── Auto rerun ────────────────────────────────────────
if (st.session_state.auto_mode and
        refresh_rate != "Manual"):
    interval = int(refresh_rate[:-1])
    time.sleep(interval)
    st.rerun()