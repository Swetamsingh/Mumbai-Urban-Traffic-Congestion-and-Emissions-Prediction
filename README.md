
# Mumbai Urban Traffic Congestion and Emissions Prediction

> **Project implementation update:** This project is focused on the **Mumbai urban region, Maharashtra, India**, and uses a **React + Vite frontend with a Python FastAPI backend**. The Streamlit instructions later in this original blueprint are superseded by the full-stack instructions in this section. Use regular CSS; Tailwind is not required.

## Mumbai study area

Define the exact geography in the final report. A reasonable starting scope is a selected set of Mumbai urban road corridors for which data can actually be obtained. Potential corridors to investigate include the Western Express Highway, Eastern Express Highway, LBS Marg, and selected links near Bandra–Kurla Complex. These are candidate study areas only—not confirmation that historical traffic-speed data is publicly available for each road.

Do not describe a small set of road sensors as representative of all Mumbai or the entire Mumbai Metropolitan Region. Record each dataset's geographic coverage, collection period, units, source, license, and limitations.

### Mumbai data acquisition plan

1. Check official civic and government open-data portals for traffic counts, road attributes, travel-time observations, incidents, and related transport data.
2. Investigate relevant transport/highway authorities and research datasets for traffic observations; verify access and reuse terms.
3. Use a documented weather source only when its time and spatial resolution are suitable for the selected roads.
4. Use OpenStreetMap for road geometry if useful, while following attribution and applicable ODbL obligations. Road geometry by itself is not traffic-speed data.
5. If representative Mumbai traffic-speed data cannot be obtained, develop the pipeline with a documented public traffic dataset and clearly label any Mumbai demonstration data as illustrative. Never fabricate traffic observations or claim Mumbai-specific model validation without representative Mumbai test data.

Potential general references include [Mumbai civic portal](https://portal.mcgm.gov.in/), [data.gov.in](https://www.data.gov.in/), [OpenStreetMap](https://www.openstreetmap.org/), and [United Nations SDGs](https://sdgs.un.org/goals). Verify the exact dataset page, terms, units, and data quality before using any source.

## Full-stack architecture

```text
React + Vite Frontend
        |
        | HTTP / JSON
        v
Python FastAPI REST API
        |
        +--> Input validation (Pydantic)
        +--> Saved ML pipeline (scikit-learn / XGBoost)
        +--> Congestion classification
        +--> CO₂ estimation module
        |
        v
Traffic dataset + model metrics
```

The React application does not load the Python model directly. It calls the FastAPI backend. The backend handles data/model inference and returns JSON.

## Recommended technology stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, JavaScript, HTML, regular CSS |
| Charts | Recharts or Plotly |
| API client | Fetch API or Axios |
| Backend API | FastAPI, Uvicorn, Pydantic |
| Machine learning | Pandas, NumPy, scikit-learn; optional XGBoost |
| Model persistence | Joblib |
| Testing | Pytest; optional Vitest for frontend |
| Version control | Git and GitHub |

## Full-stack folder structure

```text
mumbai-urban-traffic-ml/
├── README.md
├── .gitignore
├── .env.example
├── configs/
│   └── config.yaml
├── data/
│   ├── README.md
│   ├── raw/
│   ├── processed/
│   └── sample/
├── models/
├── reports/
│   ├── figures/
│   └── model_metrics.json
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_experiments.ipynb
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── schemas.py
│   │   └── services/
│   │       ├── prediction.py
│   │       └── emissions.py
│   ├── src/
│   │   └── traffic_ml/
│   │       ├── __init__.py
│   │       ├── data.py
│   │       ├── features.py
│   │       ├── train.py
│   │       ├── evaluate.py
│   │       └── visualization.py
│   └── tests/
│       ├── test_data.py
│       ├── test_features.py
│       └── test_emissions.py
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api/
        │   └── trafficApi.js
        ├── components/
        │   ├── Navbar.jsx
        │   ├── SummaryCards.jsx
        │   ├── TrafficPredictionForm.jsx
        │   ├── CongestionChart.jsx
        │   ├── RoadSegmentComparison.jsx
        │   ├── EmissionsPanel.jsx
        │   └── DataSourceNote.jsx
        ├── pages/
        │   ├── Dashboard.jsx
        │   ├── PredictTraffic.jsx
        │   ├── ExploreData.jsx
        │   └── ModelPerformance.jsx
        └── styles/
            ├── global.css
            └── dashboard.css
```

### Frontend component responsibilities

- `App.jsx`: main application shell and navigation.
- `Dashboard.jsx`: project summary, data coverage, traffic trends, and high-level indicators.
- `PredictTraffic.jsx`: collect valid prediction inputs and show predicted speed/congestion.
- `ExploreData.jsx`: show historical patterns and compare supported road segments.
- `ModelPerformance.jsx`: show MAE, RMSE, R², evaluation dates, and model comparison.
- `TrafficPredictionForm.jsx`: input form with client-side validation.
- `CongestionChart.jsx`: plot observed and predicted speed/congestion.
- `RoadSegmentComparison.jsx`: compare only road segments represented in the dataset.
- `EmissionsPanel.jsx`: show estimated CO₂ with the inputs, factor, and assumptions visible.
- `trafficApi.js`: centralize API calls and error handling.
- `global.css` and `dashboard.css`: responsive styling with regular CSS.

### Backend API endpoints

Implement these endpoints in `backend/app/main.py`; they are planned interfaces, not automatically available until coded.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | API health check |
| `GET` | `/api/summary` | Dataset coverage and summary |
| `GET` | `/api/segments` | Available road-segment IDs |
| `GET` | `/api/trends` | Historical trends for charts |
| `POST` | `/api/predict` | Return predicted speed and congestion class |
| `POST` | `/api/emissions/estimate` | Estimate CO₂ from validated inputs |
| `GET` | `/api/model-metrics` | Return saved model-evaluation metrics |

Use Pydantic request/response schemas. Configure CORS for the frontend development origin, commonly `http://localhost:5173`; restrict origins appropriately in production.

### Backend dependencies

Create `backend/requirements.txt`:

```text
fastapi
uvicorn[standard]
pydantic
pandas
numpy
scikit-learn
xgboost
joblib
pyyaml
pytest
```

If you do not use XGBoost, remove it from the dependency list. Add other packages only when the implementation requires them.

### Frontend setup

Install a supported Node.js LTS release, then from the repository root run:

```bash
mkdir -p frontend
cd frontend
npm create vite@latest . -- --template react
npm install
npm install axios recharts
```

If the Vite React app already exists, skip `npm create vite@latest` and run the install commands in the existing `frontend` directory. Use regular CSS; no Tailwind setup is necessary.

Create `frontend/.env` for local development:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Vite exposes `VITE_` variables in the browser. Do not put secrets or private API keys in them.

### Run the full-stack application

**Terminal 1 — backend**, from the repository root with the Python virtual environment active:

```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

The API should run at `http://127.0.0.1:8000`, with interactive documentation normally at `http://127.0.0.1:8000/docs`.

**Terminal 2 — frontend:**

```bash
cd frontend
npm install
npm run dev
```

Vite normally serves the frontend at `http://localhost:5173`.

### Frontend-to-backend request example

In `frontend/src/api/trafficApi.js`, a minimal API client can look like:

```javascript
const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function predictTraffic(payload) {
  const response = await fetch(`${API_BASE}/api/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Traffic prediction request failed");
  }

  return response.json();
}
```

The payload must match the Pydantic schema implemented by the backend. Show loading, empty, and error states in the React UI.

## Mumbai dashboard requirements

The frontend should visibly identify the selected study region as **Mumbai urban region, Maharashtra, India** and include:

- A dataset coverage panel that names the actual corridors/locations and date range present in the data.
- A historical congestion chart by hour and weekday.
- A road-segment selector populated from real dataset IDs.
- A prediction form that asks only for features the model actually expects.
- A model-performance page showing the held-out evaluation period.
- An emissions estimator showing traffic volume, segment length, emission factor, units, source, and assumptions.
- A notice distinguishing measured observations, model predictions, and derived estimates.

Do not show a live traffic map or live traffic status unless a real, permitted, current data source is integrated. Do not use a map pin for a road location that has not been verified.

## Updated implementation order

1. Confirm the Mumbai study boundary and locate a suitable dataset.
2. Document data source, license, schema, units, and geographic coverage.
3. Clean and explore the data.
4. Create time and road-segment features without leakage.
5. Train a baseline and Random Forest model; add XGBoost only for comparison.
6. Evaluate chronologically and save metrics and the fitted pipeline.
7. Implement emissions estimation with a cited emission factor and explicit assumptions.
8. Build FastAPI request schemas and endpoints.
9. Build the React + Vite dashboard and connect it to the API.
10. Test input validation, model inference, API errors, and emissions calculations.
11. Capture screenshots and document results, limitations, and SDG impact.



---

## Original ML methodology and evaluation reference

# ML-Based Urban Traffic Congestion and Emissions Prediction

An end-to-end Machine Learning project that predicts road traffic speed
and congestion levels using historical traffic, time, weather, and
road-related features. It also estimates traffic-related CO₂ emissions
using a clearly documented calculation method.

**Primary SDG:** SDG 11 --- Sustainable Cities and Communities\
**Related SDGs:** SDG 9 --- Industry, Innovation and Infrastructure; SDG
13 --- Climate Action

> **Important:** This is a prediction and decision-support prototype,
> not a live traffic navigation system. Emissions are estimates based on
> assumptions and available inputs, not direct measurements. Clearly
> distinguish real observations from simulated or derived values in the
> UI and report.

------------------------------------------------------------------------

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Problem Statement](#problem-statement)
3.  [Objectives](#objectives)
4.  [Key Features](#key-features)
5.  [Scope and Limitations](#scope-and-limitations)
6.  [System Architecture](#system-architecture)
7.  [Technology Stack](#technology-stack)
8.  [Dataset Plan](#dataset-plan)
9.  [Repository Structure](#repository-structure)
10. [Installation](#installation)
11. [Data Preparation](#data-preparation)
12. [Feature Engineering](#feature-engineering)
13. [Model Development](#model-development)
14. [Model Evaluation](#model-evaluation)
15. [Emissions Estimation](#emissions-estimation)
16. [Streamlit Dashboard](#streamlit-dashboard)
17. [Run the Project](#run-the-project)
18. [Configuration](#configuration)
19. [Testing and Quality Checks](#testing-and-quality-checks)
20. [Implementation Roadmap](#implementation-roadmap)
21. [Expected Deliverables](#expected-deliverables)
22. [Future Enhancements](#future-enhancements)
23. [Ethics, Privacy, and Responsible
    Use](#ethics-privacy-and-responsible-use)
24. [References](#references)

------------------------------------------------------------------------

## Project Overview

Urban traffic congestion increases travel time, fuel consumption, and
transport-related emissions. This project uses historical traffic
observations and contextual information---such as hour, day, weather,
and road characteristics---to predict traffic speed and classify
congestion.

A dashboard presents predictions, peak-hour patterns, road-segment
comparisons, model performance, and estimated CO₂ emissions. The project
can be developed and evaluated with a public dataset first, then adapted
to a city-specific dataset if suitable data becomes available.

### Typical workflow

1.  Load a traffic dataset.
2.  Validate and clean the data.
3.  Create time-based and contextual features.
4.  Train a baseline model and compare it with stronger models.
5.  Evaluate on a chronological test set.
6.  Save the trained pipeline.
7.  Use the pipeline in a Streamlit dashboard.
8.  Estimate emissions using documented assumptions.
9.  Communicate uncertainty and limitations.

------------------------------------------------------------------------

## Problem Statement

Traffic managers, commuters, and urban planners need better ways to
understand recurring congestion patterns. Static summaries describe what
happened in the past but do not necessarily indicate what traffic
conditions may be like at a future time.

The project addresses this challenge by learning patterns from
historical traffic data and predicting either:

-   **Traffic speed** (for example, kilometres per hour), or
-   **Congestion class** (for example, Low, Moderate, High, or Severe).

It then estimates traffic-related emissions from predicted traffic
conditions and explicitly stated assumptions. The model should not be
described as proving that congestion causes a specific amount of
pollution; it provides an estimate based on its chosen methodology.

------------------------------------------------------------------------

## Objectives

-   Build a reproducible end-to-end ML pipeline.
-   Predict traffic speed or congestion for a road segment and time.
-   Identify peak hours and recurring congestion patterns.
-   Compare road segments and time periods.
-   Estimate CO₂ emissions with a transparent calculation.
-   Evaluate performance on unseen, later-in-time observations.
-   Provide an interactive dashboard for non-technical users.
-   Relate the project to sustainable urban mobility and climate action.

------------------------------------------------------------------------

## Key Features

### Core features

-   Traffic dataset upload or selection of a prepared dataset.
-   Data quality checks and missing-value handling.
-   Hour, weekday, weekend, and month features.
-   Traffic-speed prediction or congestion classification.
-   Congestion trend and peak-hour visualizations.
-   Road-segment comparison.
-   Model evaluation metrics and actual-versus-predicted plots.
-   CO₂ estimate with visible assumptions.
-   Exportable prediction results.

### Optional advanced features

-   Forecast several future time intervals.
-   Add weather forecasts when a reliable source is available.
-   Add a map only when reliable road coordinates or geospatial data are
    available.
-   Compare Random Forest and XGBoost against a simple baseline.
-   Add model-drift monitoring when new observations become available.

Do not claim real-time forecasting unless the application actually
receives updated data from a live source.

------------------------------------------------------------------------

## Scope and Limitations

### Initial project scope

Start with one dataset and one clearly defined target. A practical first
version predicts traffic speed and converts the prediction into a
congestion class using documented thresholds. Emissions estimation can
be a separate, clearly labelled module.

### Limitations to document

-   Public datasets may not contain weather, vehicle mix, road type, or
    emissions data.
-   Some datasets contain only aggregated traffic readings.
-   Results may not generalize to another city or road network.
-   Forecast accuracy depends on data quality and how far into the
    future predictions are made.
-   A congestion class is a project-defined category unless an official
    local definition is used.
-   Estimated emissions are not equivalent to measured emissions.
-   Missing contextual inputs must not silently be presented as observed
    facts.

------------------------------------------------------------------------

## System Architecture

``` text
Historical Traffic Dataset
          |
          v
Data Validation and Cleaning
          |
          v
Feature Engineering
(time, road, weather, lag features where valid)
          |
          v
Chronological Train / Validation / Test Split
          |
          v
Baseline Model -> Random Forest -> XGBoost (optional)
          |
          v
Evaluation and Model Selection
          |
          v
Saved Preprocessing + Model Pipeline
          |
          +---------------------------+
          |                           |
          v                           v
Traffic Prediction             Emissions Estimator
          |                           |
          +-------------+-------------+
                        |
                        v
              Streamlit Dashboard
                        |
                        v
       Trends, Comparisons, Metrics, Exports
```

### Suggested modules

-   **Data layer:** dataset loading, schema checks, cleaning.
-   **ML layer:** preprocessing, training, evaluation, model
    persistence.
-   **Prediction layer:** input validation and inference.
-   **Emissions layer:** transparent estimation calculations.
-   **UI layer:** Streamlit controls, charts, results, and explanatory
    notes.

------------------------------------------------------------------------

## Technology Stack

  Area                     Recommended tools
  ------------------------ --------------------------------------------
  Programming language     Python 3.10+
  Data processing          Pandas, NumPy
  Visualization            Matplotlib, Plotly
  ML                       Scikit-learn
  Optional boosted trees   XGBoost
  Dashboard                Streamlit
  Model persistence        Joblib
  Testing                  Pytest
  Development              VS Code, Jupyter Notebook, or Google Colab
  Version control          Git and GitHub

Keep the initial project simple. Scikit-learn's Random Forest is
sufficient for a working version; add XGBoost only after the full
pipeline works.

------------------------------------------------------------------------

## Dataset Plan

Use a real, documented dataset and record its source, license,
collection period, units, and limitations. Choose a dataset whose target
and features are actually available; do not fabricate weather or road
attributes to make the model appear more complete.

### Possible public sources

1.  **METR-LA traffic dataset** --- traffic speed readings from road
    sensors in the Los Angeles area. Commonly used for traffic
    forecasting research. It may require additional steps to obtain and
    interpret.
2.  **PeMS / Caltrans Performance Measurement System** --- California
    freeway traffic data. Access, terms, and the exact dataset format
    should be checked before use.
3.  **UCI or other public traffic datasets** --- choose a dataset only
    after confirming its schema, source, and usage terms.
4.  **City open-data portals** --- preferable when you want a local case
    study and can verify the source and update frequency.

Search for the official dataset page or repository and cite the exact
source in your report. Dataset availability and licensing may change.

### Minimum useful columns

Your exact schema depends on the selected dataset. Aim for columns such
as:

  -----------------------------------------------------------------------
  Column                  Meaning                 Example
  ----------------------- ----------------------- -----------------------
  `timestamp`             Date and time of        `2025-01-10 08:00:00`
                          observation             

  `road_segment_id`       Road or sensor          `ROAD_01`
                          identifier              

  `traffic_speed_kmh`     Observed average speed  `24.5`

  `traffic_volume`        Vehicles counted in an  `820`
                          interval, if available  

  `temperature_c`         Temperature, if         `29.0`
                          available               

  `rainfall_mm`           Rainfall, if available  `0.0`

  `road_type`             Road category, if       `arterial`
                          available               
  -----------------------------------------------------------------------

These are **illustrative names and values**, not a claim that any one
public dataset contains all these fields.

### Recommended target

For the first version, use **traffic speed** as a regression target:

``` text
Target: traffic_speed_kmh
```

If the chosen dataset reports speed in mph, convert it correctly or keep
the original unit consistently. Do not mix units.

You can derive congestion classes from speed for demonstration, but
define thresholds for the chosen use case and explain that these are
project-defined, not universal standards. If you have an official
congestion label, prefer that label.

### Data dictionary

Create `data/README.md` with:

-   Dataset name and source URL.
-   License and attribution requirements.
-   Download date and time coverage.
-   Row count and number of road segments.
-   Meaning and unit of every column.
-   Missing-value handling.
-   Any transformations performed.
-   Whether data is observed, forecast, simulated, or derived.

Do not commit a large dataset to GitHub if its license or size does not
permit it. Include download instructions instead.

------------------------------------------------------------------------

## Repository Structure

Use the following project structure:

``` text
urban-traffic-ml/
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
├── app.py
├── configs/
│   └── config.yaml
├── data/
│   ├── README.md
│   ├── raw/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   └── sample/
│       └── sample_traffic.csv
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_experiments.ipynb
├── models/
│   └── .gitkeep
├── reports/
│   ├── figures/
│   └── model_metrics.json
├── src/
│   └── traffic_ml/
│       ├── __init__.py
│       ├── data.py
│       ├── features.py
│       ├── train.py
│       ├── evaluate.py
│       ├── predict.py
│       ├── emissions.py
│       └── visualization.py
└── tests/
    ├── test_data.py
    ├── test_features.py
    └── test_emissions.py
```

### Responsibilities

-   `app.py`: Streamlit user interface.
-   `data.py`: load data and validate required columns.
-   `features.py`: time and other model features.
-   `train.py`: chronological split, pipeline training, model saving.
-   `evaluate.py`: metrics, plots, and model comparison.
-   `predict.py`: validated inference using the saved pipeline.
-   `emissions.py`: transparent emissions estimate.
-   `visualization.py`: reusable charts.
-   `configs/config.yaml`: configurable paths, target, and thresholds.
-   `tests/`: checks for expected behavior and invalid inputs.

You may begin with fewer files, but separate responsibilities as the
project grows.

------------------------------------------------------------------------

## Installation

### 1. Create the project

``` bash
mkdir urban-traffic-ml
cd urban-traffic-ml
```

Create and activate a virtual environment.

**Windows PowerShell**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux or macOS**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

If PowerShell blocks environment activation, use an approved local
execution-policy approach or run the environment's Python executable
directly. Do not change system-wide security settings unnecessarily.

### 2. Create `requirements.txt`

Start with:

``` text
pandas
numpy
scikit-learn
matplotlib
plotly
streamlit
joblib
pytest
pyyaml
```

Optional, if using XGBoost:

``` text
xgboost
```

Install the dependencies:

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Record tested package versions before final submission for
reproducibility.

### 3. Verify the environment

``` bash
python --version
python -c "import pandas, sklearn, streamlit; print('Environment ready')"
```

------------------------------------------------------------------------

## Data Preparation

Implement `src/traffic_ml/data.py` to:

1.  Read the chosen CSV or supported file format.
2.  Check that required columns exist.
3.  Parse timestamps using the correct format and timezone.
4.  Convert numeric columns safely.
5.  remove duplicate observations where they are genuine duplicates.
6.  Report missing values and invalid ranges.
7.  Sort observations by time and road segment.
8.  Save a cleaned dataset under `data/processed/`.

### Data validation checklist

-   Is the timestamp parseable?
-   Are timestamps in the expected timezone?
-   Are speed values non-negative and within plausible bounds?
-   Are units consistent?
-   Are road IDs missing?
-   Are there duplicate sensor/time records?
-   Are missing values concentrated in particular periods or sensors?
-   Are there gaps in time series that could affect forecasting?

Avoid blindly filling all missing values with zero. Zero speed can
represent a real traffic jam and should not be confused with missing
data.

### Example schema validation

``` python
REQUIRED_COLUMNS = [
    "timestamp",
    "road_segment_id",
    "traffic_speed_kmh",
]
```

Adapt this list to the actual dataset. If road IDs are unavailable,
remove that feature and document the limitation.

------------------------------------------------------------------------

## Feature Engineering

Implement `src/traffic_ml/features.py`.

### Time features

From the timestamp, derive:

-   `hour`
-   `day_of_week`
-   `month`
-   `is_weekend`
-   `is_rush_hour` (using a documented local definition)

Traffic patterns are cyclical. For models that benefit from cyclical
representations, encode hour and weekday using sine/cosine features
rather than assuming that hour 23 is far from hour 0.

Example:

``` python
import numpy as np
import pandas as pd

def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    timestamp = pd.to_datetime(result["timestamp"], errors="coerce")

    result["hour"] = timestamp.dt.hour
    result["day_of_week"] = timestamp.dt.dayofweek
    result["month"] = timestamp.dt.month
    result["is_weekend"] = (result["day_of_week"] >= 5).astype(int)

    result["hour_sin"] = np.sin(2 * np.pi * result["hour"] / 24)
    result["hour_cos"] = np.cos(2 * np.pi * result["hour"] / 24)

    return result
```

Validate timestamps before feature engineering and adapt timezone
handling to the dataset.

### Road and weather features

Use road type, lane count, rainfall, temperature, visibility, or wind
only if reliable values are available at prediction time. Avoid
including features that would not be known when a real forecast is made.

### Lag and rolling features

Potential features include previous speed readings and rolling averages
for the same road segment. For example:

-   Previous interval speed.
-   Speed one hour earlier.
-   Rolling average over the last 3 or 6 observations.

**Leakage warning:** Create lag and rolling features separately within
each road segment, shift values so they only use earlier observations,
and never use future readings. Split chronologically before any
operation that could use information from the test period. Explain how
missing history is handled.

------------------------------------------------------------------------

## Model Development

Implement `src/traffic_ml/train.py`.

### Step 1: Define the prediction task

Recommended initial task:

``` text
Input: road segment and information available at forecast time
Output: predicted traffic speed in km/h
Task: supervised regression
```

Do not mix speed regression and congestion classification metrics. They
are different tasks and should be evaluated separately.

### Step 2: Establish a baseline

Use a simple baseline, such as:

-   Mean speed learned from the training set, or
-   Previous observed speed, when a valid previous reading is available.

For time-series work, a persistence baseline---predicting the last
observed speed---is often informative. Ensure the baseline uses only
information available at prediction time.

### Step 3: Split data chronologically

Use earlier observations for training, a later period for validation,
and the latest period for final testing. An illustrative split is 70%
training, 15% validation, and 15% testing by time, but choose a split
that matches the dataset's duration and use case.

Do not randomly split time-series rows: that can leak future patterns
into training.

If several road sensors are present, decide whether the evaluation
should test future time periods on known roads or generalization to
unseen roads. Report which one you measured.

### Step 4: Train candidate models

Recommended progression:

1.  Baseline.
2.  Random Forest Regressor.
3.  XGBoost Regressor, optional.
4.  LSTM only if the dataset has enough sequential observations and you
    can implement a proper sequence pipeline.

Start with Random Forest. Scale numerical features only when the chosen
model or preprocessing requires it. Fit all preprocessing only on the
training data by using an ML pipeline.

### Step 5: Save the pipeline

Save the fitted preprocessing and model together using Joblib:

``` python
import joblib

joblib.dump(pipeline, "models/traffic_speed_pipeline.joblib")
```

Here, `pipeline` represents your fitted preprocessing-plus-model
pipeline. Do not load a model file from an untrusted source. Keep model
and library versions documented.

### Step 6: Store experiment results

Save metrics, model name, target units, split dates, and feature list to
`reports/model_metrics.json`. This helps make the final report
reproducible.

------------------------------------------------------------------------

## Model Evaluation

### Regression metrics

  -----------------------------------------------------------------------
  Metric                              Interpretation
  ----------------------------------- -----------------------------------
  MAE                                 Average absolute speed prediction
                                      error

  RMSE                                Penalizes larger prediction errors
                                      more strongly

  R²                                  Measures fit relative to a
                                      mean-target baseline; can be
                                      negative on test data
  -----------------------------------------------------------------------

Always report the speed unit for MAE and RMSE. Compare models on the
same held-out test period.

### Congestion classification metrics

If you also classify congestion, report:

-   Precision.
-   Recall.
-   F1-score.
-   Confusion matrix.
-   Per-class support.

Accuracy alone can be misleading if most observations belong to one
congestion class.

### Required evaluation visuals

-   Actual versus predicted speed.
-   Residual/error distribution.
-   MAE or RMSE by hour of day.
-   Error by road segment, if road IDs are available.
-   Congestion class confusion matrix, if classification is implemented.
-   Feature importance or model interpretation, with limitations
    explained.

### Acceptance criteria

Define criteria before reviewing final test results. For example:

-   The trained model must beat a reasonable baseline on the held-out
    period.
-   The test period must be later than the training period.
-   No future-derived features are used.
-   Metrics and plots can be regenerated.
-   Invalid user inputs produce helpful errors.

Do not promise a particular accuracy before measuring it.

------------------------------------------------------------------------

## Emissions Estimation

Implement `src/traffic_ml/emissions.py`.

### Recommended transparent method

A simple estimate can use:

\[ `\text{CO₂ (g)}`{=tex} = `\text{vehicle-km travelled}`{=tex}
`\times`{=tex} `\text{emission factor (g CO₂/vehicle-km)}`{=tex} \]

For a road segment:

\[ `\text{vehicle-km travelled}`{=tex} = `\text{vehicle count}`{=tex}
`\times `{=tex}`\text{segment length (km)}`{=tex} \]

If traffic volume is available for a defined interval and segment length
is known, this gives an estimated total for that interval. Clearly state
whether the volume represents vehicles per interval, vehicles per hour,
or another measure.

### Important assumptions

-   The emission factor depends on vehicle type, fuel, speed, vehicle
    age, and local conditions.
-   A single average factor is a simplification.
-   If traffic volume or segment length is unavailable, do not present a
    precise total-emissions number as if it were measured.
-   If you use a published emission factor, cite its authoritative
    source, year, units, vehicle category, and assumptions.
-   If you use an illustrative factor for a prototype, label it as
    illustrative and make it configurable.
-   Avoid converting predicted speed directly into CO₂ without a
    defensible speed-emissions relationship.
-   If estimating the effect of congestion, define a comparison scenario
    and avoid claiming causal impact unless the methodology supports it.

### Emissions output should show

-   Estimated CO₂ in grams or kilograms.
-   Period covered by the estimate.
-   Vehicle count and segment length used, if available.
-   Emission factor and its source.
-   Assumptions and uncertainty warning.

Consider adding fuel consumption or pollutant estimates only if there is
an appropriate, documented methodology and data.

------------------------------------------------------------------------

## Streamlit Dashboard

Implement the user interface in `app.py`.

### Suggested pages or sections

#### 1. Overview

-   Project purpose and SDG alignment.
-   Dataset source and coverage.
-   Clear note about whether the data is historical, simulated, or live.

#### 2. Explore Data

-   Dataset preview.
-   Missing-value summary.
-   Speed distribution.
-   Traffic trends by hour and day.
-   Road-segment comparisons, when supported by the dataset.

#### 3. Predict Traffic

-   Select a road segment if available.
-   Select a forecast timestamp.
-   Enter or select only the input features required by the trained
    model.
-   Show predicted speed and congestion category.
-   Display the model's supported prediction horizon.

Do not ask the user to enter features that the model was not trained to
accept. Do not silently fill unavailable future weather with historical
or fabricated values.

#### 4. Congestion Analysis

-   Peak-hour patterns.
-   Observed versus predicted traffic.
-   Road/time comparisons.
-   Model uncertainty or limitations where available.

#### 5. Emissions Estimator

-   Input traffic volume, segment length, and a sourced/configurable
    emission factor.
-   Display estimated CO₂ and assumptions.
-   Clearly separate the emissions calculation from the ML prediction.

#### 6. Model Performance

-   MAE, RMSE, and R².
-   Baseline comparison.
-   Actual-versus-predicted chart.
-   Evaluation period and dataset description.

### Example dashboard launch

``` bash
streamlit run app.py
```

The dashboard should validate user input and show a useful error if the
model, data, or required columns are unavailable.

------------------------------------------------------------------------

## Run the Project

Once the modules are implemented, a typical workflow could be:

``` bash
# 1. Activate the virtual environment first

# 2. Install dependencies
pip install -r requirements.txt

# 3. Explore the dataset in notebooks/
# Run notebooks in numerical order.

# 4. Clean and prepare data
python -m traffic_ml.data

# 5. Train the model
python -m traffic_ml.train

# 6. Evaluate the model
python -m traffic_ml.evaluate

# 7. Launch the dashboard
streamlit run app.py

# 8. Run tests
pytest -q
```

These commands assume you package the code under `src/traffic_ml` and
implement command-line entry points for the modules. Until those entry
points are written, run the relevant scripts directly or configure the
package for installation with `pip install -e .`.

A recommended `pyproject.toml` can be added later to define the package
and command-line tools.

------------------------------------------------------------------------

## Configuration

Store non-secret settings in `configs/config.yaml`. For example:

``` yaml
data:
  input_path: "data/raw/traffic.csv"
  processed_path: "data/processed/traffic_clean.csv"
  timestamp_column: "timestamp"
  road_id_column: "road_segment_id"
  target_column: "traffic_speed_kmh"

training:
  test_fraction: 0.15
  validation_fraction: 0.15
  random_state: 42
  model_type: "random_forest"

congestion:
  # Example thresholds only; adapt and justify for the selected city/dataset.
  low_speed_max_kmh: 40
  moderate_speed_min_kmh: 20
```

The example thresholds are placeholders, not recommended universal
definitions. Design non-overlapping class boundaries in code and
document them. Check that the configuration reflects the actual dataset
before running training.

Never store passwords, access tokens, or private API keys in the
repository. Use environment variables for secrets.

------------------------------------------------------------------------

## Testing and Quality Checks

Add tests for:

-   Missing required columns.
-   Invalid timestamps.
-   Duplicate rows and missing values.
-   Feature creation around midnight and week boundaries.
-   Lag features not using future data.
-   Model predictions being finite numeric values.
-   Emissions estimates using compatible units.
-   Invalid negative traffic volumes or segment lengths.
-   Dashboard behavior when no trained model exists.

### Example test cases

``` text
test_data.py
- raises a clear error if timestamp is missing
- handles invalid timestamps explicitly
- reports missing target values

test_features.py
- extracts hour and weekday correctly
- creates cyclical features within expected bounds
- calculates lags separately by road segment

test_emissions.py
- calculates vehicle-km correctly
- calculates CO₂ from a documented factor
- rejects negative volume or distance
```

------------------------------------------------------------------------

## Implementation Roadmap

  -----------------------------------------------------------------------
  Phase                   Tasks                   Deliverable
  ----------------------- ----------------------- -----------------------
  1\. Define              Choose city/use case,   Project scope and data
                          target, and dataset     dictionary

  2\. Explore             Inspect schema, units,  EDA notebook
                          missing values, and     
                          trends                  

  3\. Prepare             Clean records and       Reproducible
                          create valid time       preprocessing
                          features                

  4\. Model               Establish baseline and  Saved pipeline
                          train Random Forest     

  5\. Evaluate            Test chronologically    Metrics JSON and
                          and compare metrics     figures

  6\. Emissions           Implement               Emissions module
                          sourced/configurable    
                          estimate                

  7\. Dashboard           Build prediction and    Streamlit application
                          analysis UI             

  8\. Verify              Test edge cases and     Test results
                          reproduce results       

  9\. Document            Record data source,     Final README and report
                          assumptions,            
                          limitations, and SDGs   

  10\. Present            Demonstrate a complete  Demo and presentation
                          example from input to   
                          result                  
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## Expected Deliverables

At project completion, the repository should contain:

-   [ ] A dataset source and data dictionary.
-   [ ] Data exploration notebook.
-   [ ] Reproducible preprocessing and feature engineering.
-   [ ] Baseline and at least one trained ML model.
-   [ ] Chronological test results with suitable metrics.
-   [ ] Saved model pipeline and model metadata.
-   [ ] Streamlit dashboard.
-   [ ] Transparent emissions estimation module.
-   [ ] Unit tests and instructions to run them.
-   [ ] Screenshots or a short demo.
-   [ ] Internship report with methodology, results, limitations, and
    SDG mapping.
-   [ ] Dataset and third-party attribution.

### Suggested final demonstration

1.  Open the dashboard.
2.  Show the dataset source and coverage.
3.  Explore a peak-hour traffic pattern.
4.  Select a supported road/time input and predict speed.
5.  Compare prediction with the observed value where available.
6.  Show the model's test metrics.
7.  Demonstrate an emissions estimate and explain the assumptions.
8.  Explain how better traffic information can support sustainable urban
    planning.

------------------------------------------------------------------------

## Future Enhancements

-   Integrate verified city traffic APIs or road-sensor feeds.
-   Incorporate weather forecasts available at prediction time.
-   Add geospatial visualization when reliable coordinates are
    available.
-   Train a multi-step forecasting model.
-   Investigate graph-based neural networks for connected road networks.
-   Add uncertainty intervals and monitor model drift.
-   Evaluate performance across road types and time periods.
-   Compare alternative emissions methodologies with documented sources.
-   Deploy the application with appropriate resource and security
    controls.

------------------------------------------------------------------------

## Ethics, Privacy, and Responsible Use

-   Prefer aggregated traffic data and avoid collecting personal
    identifiers.
-   Follow dataset licenses and API terms.
-   Do not expose sensitive infrastructure information.
-   Describe model performance honestly and include known failure cases.
-   Avoid presenting predictions as guaranteed traffic conditions.
-   Make clear that estimated emissions are not official measurements.
-   Assess whether errors disproportionately affect particular areas or
    road users.
-   Do not recommend interventions solely from model output without
    local context and human review.

------------------------------------------------------------------------

## References

Add the exact sources you used and the access date in your final
submission. Potential starting points:

-   United Nations Sustainable Development Goals:
    https://sdgs.un.org/goals
-   California Department of Transportation (Caltrans):
    https://dot.ca.gov/
-   Caltrans Performance Measurement System (PeMS):
    https://pems.dot.ca.gov/
-   Scikit-learn documentation: https://scikit-learn.org/stable/
-   Streamlit documentation: https://docs.streamlit.io/
-   XGBoost documentation: https://xgboost.readthedocs.io/
-   TensorFlow documentation, if using an LSTM:
    https://www.tensorflow.org/

Verify the precise dataset landing page, data license, emission-factor
source, and relevant documentation before submitting. Cite the specific
dataset and emission-factor documents rather than only a general
homepage.

------------------------------------------------------------------------

## License

Choose a license for your own code after checking the licenses and terms
of the datasets, model artifacts, and other third-party components you
include. A code license does not automatically grant rights to
redistribute third-party data.
