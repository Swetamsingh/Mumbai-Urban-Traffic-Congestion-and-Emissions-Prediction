from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from traffic_ml.data import load_or_generate_sample_data, validate_and_clean
from traffic_ml.emissions import estimate_emissions
from traffic_ml.features import classify_congestion
from traffic_ml.predict import predict_traffic
from traffic_ml.train import train_model

st.set_page_config(page_title="Urban Traffic Congestion Prediction", page_icon="🚦", layout="wide")


def load_config():
    with open(ROOT / "configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


CONFIG = load_config()

st.title("Urban Traffic Congestion and Emissions Prediction")
st.markdown(
    "This prototype predicts traffic speed and estimates CO₂ emissions using a transparent, documented formula. "
    "It is a decision-support tool, not a live traffic control system."
)

# Data overview
raw_data = load_or_generate_sample_data(ROOT / CONFIG["data"]["input_path"])
cleaned_data = validate_and_clean(raw_data, CONFIG["data"]["timestamp_column"], CONFIG["data"]["road_id_column"], CONFIG["data"]["target_column"])

st.subheader("1. Dataset overview")
col1, col2, col3 = st.columns(3)
col1.metric("Rows", len(cleaned_data))
col2.metric("Road segments", cleaned_data[CONFIG["data"]["road_id_column"]].nunique())
col3.metric("Speed range", f"{cleaned_data[CONFIG['data']['target_column']].min():.1f}–{cleaned_data[CONFIG['data']['target_column']].max():.1f} km/h")

st.dataframe(cleaned_data.head(10), width="stretch")

# Model section
st.subheader("2. Train and evaluate the model")
if st.button("Train model"):
    with st.spinner("Training the pipeline..."):
        metrics = train_model(ROOT / "configs/config.yaml")
    st.success("Model trained successfully.")
    st.json(metrics)

model_path = ROOT / CONFIG["data"]["model_path"]
if model_path.exists():
    st.subheader("3. Predict traffic")
    road_options = sorted(cleaned_data[CONFIG["data"]["road_id_column"]].unique().tolist())
    road = st.selectbox("Road segment", road_options)
    selected_row = cleaned_data[cleaned_data[CONFIG["data"]["road_id_column"]] == road].sort_values(CONFIG["data"]["timestamp_column"]).iloc[-1]
    timestamp = st.datetime_input(
        "Prediction timestamp",
        value=pd.to_datetime(selected_row[CONFIG["data"]["timestamp_column"]]) + pd.Timedelta(hours=1),
    )
    volume = st.number_input("Traffic volume (vehicles)", min_value=0, value=int(selected_row.get("traffic_volume", 500)))
    temp = st.number_input("Temperature (°C)", value=float(selected_row.get("temperature_c", 22)))
    rainfall = st.number_input("Rainfall (mm)", min_value=0.0, value=float(selected_row.get("rainfall_mm", 0.0)))

    sample = pd.DataFrame([
        {
            CONFIG["data"]["timestamp_column"]: pd.Timestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            CONFIG["data"]["road_id_column"]: road,
            "traffic_volume": volume,
            "temperature_c": temp,
            "rainfall_mm": rainfall,
            "road_type": selected_row.get("road_type", "arterial"),
        }
    ])

    if st.button("Predict"):
        history = cleaned_data[
            (cleaned_data[CONFIG["data"]["road_id_column"]] == road)
            & (cleaned_data[CONFIG["data"]["timestamp_column"]] < pd.Timestamp(timestamp))
        ]
        with st.spinner("Running prediction..."):
            results = predict_traffic(
                model_path,
                sample,
                CONFIG["data"]["target_column"],
                history=history,
            )
        pred_speed = float(results.iloc[0]["predicted_speed"])
        status = classify_congestion(pred_speed, CONFIG["congestion"]["low_speed_max_kmh"], CONFIG["congestion"]["moderate_speed_min_kmh"])
        st.metric("Predicted speed", f"{pred_speed:.1f} km/h")
        st.metric("Congestion status", status)

st.subheader("4. Emissions estimator")
st.caption("CO₂ = vehicle count × segment length × emission factor. The default factor is illustrative, not a measured or sourced local value.")
vehicle_count = st.number_input("Vehicle count", min_value=0, value=500)
segment_length = st.number_input("Segment length (km)", min_value=0.0, value=2.0)
emission_factor = st.number_input("Emission factor (g CO₂/vehicle-km)", min_value=0.0, value=180.0)
if st.button("Estimate emissions"):
    estimate = estimate_emissions(vehicle_count, segment_length, emission_factor)
    st.metric("Estimated CO₂", f"{estimate['co2_kg']:.2f} kg")
    st.json({
        "co2_grams": round(estimate["co2_grams"], 2),
        "co2_kg": round(estimate["co2_kg"], 2),
        "assumption": "Prototype estimate based on a constant emission factor and segment length.",
    })

st.caption("Note: This dashboard uses a synthetic sample dataset for demonstration and should not be interpreted as live traffic information.")
