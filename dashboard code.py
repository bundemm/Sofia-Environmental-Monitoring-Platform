import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Sofia Environmental Dashboard",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("Sofia Environmental Dashboard")

# =========================================================
# LOAD DATA
# =========================================================

DATA_PATH = Path("all_nodes_combined.csv")

@st.cache_data
def load_data():

    df = pd.read_csv(DATA_PATH, low_memory=False)

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Timestamp
    df["timestamp"] = pd.to_datetime(df["time"], errors="coerce")

    # Numeric columns
    numeric_columns = [
        "gamma_cpm",
        "gamma_raw",
        "pm10",
        "pm2.5",
        "relative humidity"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # District column
    df["district"] = df["location"]

    return df

# Load data
df = load_data()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Controls")

metric = st.sidebar.selectbox(
    "Choose Metric",
    [
        "Gamma",
        "PM10",
        "PM2.5",
        "Humidity"
    ]
)

districts = sorted(df["district"].dropna().unique())

selected_districts = st.sidebar.multiselect(
    "Select Districts",
    districts,
    default=districts[:5]
)

# =========================================================
# FILTER DATA
# =========================================================

filtered_df = df[df["district"].isin(selected_districts)]

# =========================================================
# GAMMA
# =========================================================

if metric == "Gamma":

    st.subheader("Gamma Radiation")

    fig = go.Figure()

    for district in selected_districts:

        local = filtered_df[filtered_df["district"] == district]

        # CPM
        fig.add_trace(
            go.Scatter(
                x=local["timestamp"],
                y=local["gamma_cpm"],
                mode="lines",
                line=dict(width=0.5),
                name=f"{district} CPM"
            )
        )

        # RAW
        fig.add_trace(
            go.Scatter(
                x=local["timestamp"],
                y=local["gamma_raw"],
                mode="lines",
                line=dict(width=0.5),
                name=f"{district} RAW"
            )
        )

    fig.update_layout(
        template="plotly_white",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# PM10
# =========================================================

elif metric == "PM10":

    st.subheader("PM10")

    fig = px.line(
        filtered_df,
        x="timestamp",
        y="pm10",
        color="district"
    )

    fig.update_traces(line=dict(width=0.5))

    fig.update_layout(
        template="plotly_white",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# PM2.5
# =========================================================

elif metric == "PM2.5":

    st.subheader("PM2.5")

    fig = px.line(
        filtered_df,
        x="timestamp",
        y="pm2.5",
        color="district"
    )

    fig.update_traces(line=dict(width=0.5))

    fig.update_layout(
        template="plotly_white",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# HUMIDITY
# =========================================================

elif metric == "Humidity":

    st.subheader("Humidity")

    fig = px.line(
        filtered_df,
        x="timestamp",
        y="relative humidity",
        color="district"
    )

    fig.update_traces(line=dict(width=0.5))

    fig.update_layout(
        template="plotly_white",
        height=700
    )

    st.plotly_chart(fig, use_container_width=True)