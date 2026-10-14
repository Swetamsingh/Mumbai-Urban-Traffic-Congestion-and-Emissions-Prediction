from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd


def plot_actual_vs_predicted(df: pd.DataFrame, actual_col: str = "traffic_speed_kmh", pred_col: str = "predicted_speed"):
    plt.figure(figsize=(8, 5))
    plt.scatter(df[actual_col], df[pred_col], alpha=0.7)
    min_val = min(df[actual_col].min(), df[pred_col].min())
    max_val = max(df[actual_col].max(), df[pred_col].max())
    plt.plot([min_val, max_val], [min_val, max_val], "--", color="gray")
    plt.xlabel("Actual speed (km/h)")
    plt.ylabel("Predicted speed (km/h)")
    plt.title("Actual vs Predicted Speed")
    plt.tight_layout()
    return plt.gcf()


def plot_speed_by_hour(df: pd.DataFrame, hour_col: str = "hour", speed_col: str = "traffic_speed_kmh"):
    hourly = df.groupby(hour_col)[speed_col].mean().sort_index()
    plt.figure(figsize=(9, 4))
    hourly.plot(kind="line", marker="o")
    plt.xlabel("Hour of day")
    plt.ylabel("Average speed (km/h)")
    plt.title("Average Speed by Hour")
    plt.tight_layout()
    return plt.gcf()
