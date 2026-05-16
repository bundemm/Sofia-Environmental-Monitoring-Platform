import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Sofia Environmental Dashboard",
    layout="wide"
)

# =========================================================
# IMAGE TO BASE64
# =========================================================

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

BASE_DIR = Path(__file__).parent

earth_img = get_base64(BASE_DIR / "earth_heart.png")
background_img = get_base64(BASE_DIR / "background.png")

# =========================================================
# GLOBAL STYLES
# =========================================================

st.markdown(
    f"""
    <style>

    /* =====================================================
       APP BACKGROUND
    ===================================================== */

    .stApp {{
        background-image:
            linear-gradient(
                rgba(0,0,0,0.38),
                rgba(0,0,0,0.38)
            ),
            url("data:image/png;base64,{background_img}");

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* =====================================================
       TRANSPARENT HEADER
    ===================================================== */

    header[data-testid="stHeader"] {{
        background: rgba(0,0,0,0) !important;
    }}

    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {{
        background:
            linear-gradient(
                180deg,
                rgba(5,10,20,0.96),
                rgba(5,12,18,0.94)
            ) !important;

        border-right:
            1px solid rgba(255,255,255,0.08);
    }}

    .block-container {{
        padding-top: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }}

    h1,h2,h3,h4,h5,h6,p,label,span {{
        color:white !important;
    }}

    /* =====================================================
       SIDEBAR LOGO
    ===================================================== */

    .sidebar-logo {{
        width:110px;
        height:110px;
        border-radius:50%;
        object-fit:cover;
        display:block;
        margin:auto;
        margin-top:18px;
        margin-bottom:18px;

        box-shadow:
            0 0 30px rgba(164,255,93,0.55);
    }}

    /* =====================================================
       SIDEBAR TITLE
    ===================================================== */

    .sidebar-title {{
        color:white;
        font-size:28px;
        font-weight:900;
        text-align:center;
        line-height:1.18;
        margin-bottom:28px;
    }}

    /* =====================================================
       DRAG DROP BOX
    ===================================================== */

    .upload-box {{

        border:
            2px dashed rgba(255,255,255,0.16);

        border-radius:24px;

        background:
            rgba(255,255,255,0.04);

        padding:28px 18px;

        text-align:center;

        backdrop-filter:blur(14px);

        margin-bottom:20px;
    }}

    .upload-icon {{
        font-size:58px;
        color:#d8d8a6;
        margin-bottom:10px;
    }}

    .upload-text {{
        color:white;
        font-size:18px;
        line-height:1.5;
        font-weight:500;
    }}

    .upload-subtext {{
        color:rgba(255,255,255,0.65);
        margin-top:12px;
        font-size:14px;
    }}

    /* =====================================================
       KPI CARDS
    ===================================================== */

    .metric-card {{
        background:
            rgba(255,255,255,0.12);

        border-radius:22px;

        padding:24px;

        backdrop-filter:blur(16px);

        border:
            1px solid rgba(255,255,255,0.12);

        min-height:120px;
    }}

    .metric-title {{
        color:white;
        font-size:20px;
        font-weight:500;
        margin-bottom:14px;
    }}

    .metric-value {{
        color:white !important;
        font-size:42px !important;
        font-weight:900 !important;
        line-height:1.1 !important;
    }}

    /* =====================================================
       TABLE
    ===================================================== */

    .stDataFrame {{
        background:
            rgba(0,0,0,0.45);

        border-radius:20px;
        overflow:hidden;
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# SIDEBAR HEADER
# =========================================================

st.sidebar.markdown(
    f"""
    <img class="sidebar-logo"
    src="data:image/png;base64,{earth_img}">

    <div class="sidebar-title">
        Sofia Environmental Dashboard
    </div>
    """,
    unsafe_allow_html=True
)

# =========================================================
# FILE UPLOADER
# =========================================================

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

st.sidebar.markdown(
"""
<div class="upload-box">

<div class="upload-icon">
⭱
</div>

<div class="upload-text">
Drag and drop CSV file here<br>
or click Browse files above
</div>

<div class="upload-subtext">
CSV files supported
</div>

</div>
""",
    unsafe_allow_html=True
)

# =========================================================
# LOAD DATA
# =========================================================

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

    except:
        df = pd.read_csv(
            uploaded_file,
            sep=";"
        )

else:

    try:
        df = pd.read_csv(
            "all_nodes_combined.csv"
        )

    except:
        st.error(
            "all_nodes_combined.csv not found"
        )
        st.stop()

# =========================================================
# CLEAN COLUMNS
# =========================================================

df.columns = [
    str(c).strip()
    for c in df.columns
]

# =========================================================
# DETECT COLUMNS
# =========================================================

date_col = None
location_col = None

temp_col = None
humidity_col = None
pm10_col = None
pm25_col = None
gamma_col = None

for col in df.columns:

    c = col.lower()

    if c in [
        "time",
        "date",
        "timestamp"
    ]:
        date_col = col

    # =========================================================
# DETECT COLUMNS
# =========================================================

date_col = None
location_col = None
node_col = None

temp_col = None
humidity_col = None
pm10_col = None
pm25_col = None
gamma_col = None

for col in df.columns:

    c = col.lower().strip()

    # DATE COLUMN
    if c in [
        "time",
        "date",
        "timestamp"
    ]:
        date_col = col

    # DISTRICT / LOCATION NAME
    if c in [
        "location",
        "district",
        "district_name",
        "name",
        "area",
        "neighbourhood"
    ]:
        location_col = col

    # NODE COLUMN
    if c in [
        "node",
        "node_id",
        "sensor",
        "station"
    ]:
        node_col = col

    # METRICS
    if "temp" in c:
        temp_col = col

    if "humidity" in c:
        humidity_col = col

    if c == "pm10":
        pm10_col = col

    if "pm2.5" in c or "pm25" in c:
        pm25_col = col

    if "gamma" in c:
        gamma_col = col

    if "temp" in c:
        temp_col = col

    if "humidity" in c:
        humidity_col = col

    if c == "pm10":
        pm10_col = col

    if "pm2.5" in c or "pm25" in c:
        pm25_col = col

    if "gamma" in c:
        gamma_col = col

# =========================================================
# NUMERIC CLEAN
# =========================================================

numeric_cols = [
    temp_col,
    humidity_col,
    pm10_col,
    pm25_col,
    gamma_col
]

for col in numeric_cols:

    if col and col in df.columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

# =========================================================
# METRIC SELECTOR
# =========================================================

metric_map = {}

if temp_col:
    metric_map["Temperature"] = temp_col

if humidity_col:
    metric_map["Humidity"] = humidity_col

if pm10_col:
    metric_map["PM10"] = pm10_col

if pm25_col:
    metric_map["PM2.5"] = pm25_col

if gamma_col:
    metric_map["Gamma"] = gamma_col

selected_metric = st.sidebar.selectbox(
    "Select Metric",
    list(metric_map.keys())
)

metric_col = metric_map[selected_metric]

# =========================================================
# DISTRICT FILTER
# =========================================================

if location_col:

    district_values = (
        df[location_col]
        .dropna()
        .astype(str)
        .sort_values()
        .unique()
    )

    selected_locations = st.sidebar.multiselect(
        "Select Districts",
        district_values,
        default=list(district_values[:5])
    )

    filtered = df[
        df[location_col]
        .astype(str)
        .isin(selected_locations)
    ]

else:
    filtered = df.copy()

# =========================================================
# MAIN TITLE
# =========================================================

st.markdown(
"""
<div style="
color:white;
font-size:58px;
font-weight:900;
line-height:1.08;
margin-bottom:10px;
">
Sofia Environmental Monitoring Platform
</div>

<div style="
color:rgba(255,255,255,0.92);
font-size:22px;
margin-bottom:36px;
">
    Interactive ecological monitoring of Sofia districts.
</div>
""",
    unsafe_allow_html=True
)

# =========================================================
# SAFE KPI
# =========================================================

def safe_mean(column):

    if column is None:
        return 0

    try:

        vals = pd.to_numeric(
            filtered[column],
            errors="coerce"
        ).dropna()

        if len(vals) == 0:
            return 0

        return round(vals.mean(), 2)

    except:
        return 0

avg_temp = safe_mean(temp_col)
avg_humidity = safe_mean(humidity_col)
avg_pm10 = safe_mean(pm10_col)
avg_pm25 = safe_mean(pm25_col)
avg_gamma = safe_mean(gamma_col)

# =========================================================
# KPI ROW
# =========================================================

c1, c2, c3, c4, c5 = st.columns(5)

def metric_card(title, value):

    st.markdown(
f"""
<div class="metric-card">
<div class="metric-title">{title}</div>
<div class="metric-value">{value}</div>
</div>
""",
        unsafe_allow_html=True
    )

with c1:
    metric_card(
        "🌡 Avg Temp",
        f"{avg_temp} °C"
    )

with c2:
    metric_card(
        "💧 Avg Humidity",
        f"{avg_humidity} %"
    )

with c3:
    metric_card(
        "〰 Avg PM10",
        f"{avg_pm10}"
    )

with c4:
    metric_card(
        "〰 Avg PM2.5",
        f"{avg_pm25}"
    )

with c5:
    metric_card(
        "☢ Avg Gamma",
        f"{avg_gamma}"
    )

# =========================================================
# DYNAMIC GRAPH TITLE
# =========================================================

st.markdown(
    f"## 📈 {selected_metric} Analysis"
)

# =========================================================
# DATE PARSE
# =========================================================

if date_col:

    filtered[date_col] = pd.to_datetime(
        filtered[date_col],
        errors="coerce"
    )

# =========================================================
# GRAPH
# =========================================================

if (
    date_col
    and location_col
    and metric_col
):

    chart_df = filtered.copy()

    chart_df = chart_df.dropna(
        subset=[
            date_col,
            metric_col
        ]
    )

    district_avg = (
        chart_df
        .groupby(
            [
                pd.Grouper(
                    key=date_col,
                    freq="D"
                ),
                location_col
            ]
        )[metric_col]
        .mean()
        .reset_index()
    )

    sofia_avg = (
        chart_df
        .groupby(
            pd.Grouper(
                key=date_col,
                freq="D"
            )
        )[metric_col]
        .mean()
        .reset_index()
    )

    fig = px.line(
        district_avg,
        x=date_col,
        y=metric_col,
        color=location_col,
        template="plotly_white"
    )

    fig.add_trace(
        go.Scatter(
            x=sofia_avg[date_col],
            y=sofia_avg[metric_col],
            mode="lines",
            name="Sofia Daily Average",

            line=dict(
                color="black",
                width=4
            )
        )
    )

    fig.update_layout(
        height=560,

        paper_bgcolor=
            "rgba(255,255,255,0.96)",

        plot_bgcolor=
            "rgba(255,255,255,0.96)",

        font=dict(
            color="black",
            size=14
        ),

        xaxis=dict(
            title="Time",
            title_font=dict(
                color="black"
            ),
            tickfont=dict(
                color="black"
            ),
            gridcolor=
                "rgba(0,0,0,0.15)"
        ),

        yaxis=dict(
            title=metric_col,
            title_font=dict(
                color="black"
            ),
            tickfont=dict(
                color="black"
            ),
            gridcolor=
                "rgba(0,0,0,0.15)"
        ),

        legend=dict(
            font=dict(
                color="black"
            ),

            bgcolor=
                "rgba(255,255,255,0.72)"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# TABLE
# =========================================================

st.markdown(
    "## 📄 Show Filtered Data"
)

st.dataframe(
    filtered,
    use_container_width=True,
    height=420
)

# =========================================================
# DOWNLOAD
# =========================================================

csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.sidebar.download_button(
    "⬇ Download Filtered CSV",
    csv,
    "filtered_sofia_environment.csv",
    "text/csv"
)
