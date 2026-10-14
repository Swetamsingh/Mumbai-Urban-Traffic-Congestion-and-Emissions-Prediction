import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getModelMetrics } from "../api/trafficApi.js";
import DataSourceNote from "../components/DataSourceNote.jsx";

function MetricTile({ label, value, unit, detail }) {
  return <div className="metric-tile"><span>{label}</span><strong>{value}<small>{unit}</small></strong><p>{detail}</p></div>;
}

export default function ModelPerformance() {
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getModelMetrics().then(setMetrics).catch((requestError) => setError(requestError.message));
  }, []);

  const comparison = metrics?.baseline ? [
    { name: "Random Forest", mae: metrics.mae },
    { name: "Persistence baseline", mae: metrics.baseline.mae },
  ] : [];

  return (
    <div className="page-content">
      <div className="page-heading-row">
        <div><div className="eyebrow"><span className="eyebrow-dot" /> CHRONOLOGICAL TEST SET</div><h1>Model performance</h1><p className="page-description">Held-out results on a later period for the available demonstration dataset.</p></div>
        {metrics?.model_name && <span className="model-badge">{metrics.model_name}</span>}
      </div>
      <DataSourceNote compact />
      {error && <div className="error-banner" role="alert">{error}</div>}
      {!metrics ? <div className="loading-block">Loading model metrics…</div> : !metrics.available ? (
        <div className="empty-state"><h2>No saved evaluation yet</h2><p>{metrics.message}</p><code>python -m traffic_ml.train</code></div>
      ) : (
        <>
          <section className="metrics-grid">
            <MetricTile label="MAE" value={Number(metrics.mae).toFixed(2)} unit=" km/h" detail="Average absolute speed error" />
            <MetricTile label="RMSE" value={Number(metrics.rmse).toFixed(2)} unit=" km/h" detail="Penalizes larger errors" />
            <MetricTile label="R²" value={Number(metrics.r2).toFixed(3)} unit="" detail="Fit relative to mean prediction" />
            <MetricTile label="Test rows" value={metrics.test_rows.toLocaleString()} unit="" detail="Later-in-time observations" />
          </section>
          <section className="performance-grid">
            <div className="chart-panel">
              <div className="panel-heading"><div><h2>MAE vs. persistence baseline</h2><p>Lower error is better · same held-out period</p></div><span className="chart-unit">KM/H</span></div>
              <div className="chart-wrap">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={comparison} layout="vertical" margin={{ top: 10, right: 20, bottom: 0, left: 18 }}>
                    <CartesianGrid stroke="#e8eeeb" strokeDasharray="3 5" horizontal={false} />
                    <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: "#788681", fontSize: 11 }} />
                    <YAxis type="category" dataKey="name" width={125} axisLine={false} tickLine={false} tick={{ fill: "#52625b", fontSize: 11 }} />
                    <Tooltip formatter={(value) => [`${Number(value).toFixed(2)} km/h`, "MAE"]} contentStyle={{ border: "1px solid #dfe7e2", borderRadius: 8 }} />
                    <Bar dataKey="mae" fill="#137a65" radius={[0, 4, 4, 0]} maxBarSize={30} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <section className="evaluation-details">
              <span className="result-kicker">EVALUATION WINDOW</span>
              <strong>{new Date(metrics.test_start).toLocaleDateString()} — {new Date(metrics.test_end).toLocaleDateString()}</strong>
              <dl className="result-details">
                <div><dt>Model</dt><dd>{metrics.model_name}</dd></div>
                <div><dt>Target</dt><dd>{metrics.target} ({metrics.unit})</dd></div>
                <div><dt>Validation rows</dt><dd>{metrics.validation_rows}</dd></div>
                <div><dt>Test rows</dt><dd>{metrics.test_rows}</dd></div>
                <div><dt>Baseline MAE</dt><dd>{Number(metrics.baseline.mae).toFixed(2)} km/h</dd></div>
              </dl>
            </section>
          </section>
          <p className="footnote">These scores describe only the synthetic sample's held-out period. They are not evidence of accuracy on Mumbai roads.</p>
        </>
      )}
    </div>
  );
}
