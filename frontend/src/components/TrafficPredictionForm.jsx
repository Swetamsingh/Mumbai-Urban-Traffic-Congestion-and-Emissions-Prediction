import { useEffect, useState } from "react";
import { ArrowUpRight, LoaderCircle } from "lucide-react";
import { predictTraffic } from "../api/trafficApi.js";

function nextHour(value) {
  if (!value) return "";
  const date = new Date(value);
  date.setHours(date.getHours() + 1);
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return local.toISOString().slice(0, 16);
}

export default function TrafficPredictionForm({ segments, summary }) {
  const [segmentId, setSegmentId] = useState("");
  const [forecastTimestamp, setForecastTimestamp] = useState("");
  const [trafficVolume, setTrafficVolume] = useState("");
  const [temperature, setTemperature] = useState("");
  const [rainfall, setRainfall] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (segments.length && !segments.some((segment) => segment.road_segment_id === segmentId)) {
      setSegmentId(segments[0].road_segment_id);
    }
  }, [segments, segmentId]);

  useEffect(() => {
    setForecastTimestamp(nextHour(summary?.coverage_end));
  }, [summary?.coverage_end]);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    const payload = {
      road_segment_id: segmentId,
      forecast_timestamp: forecastTimestamp,
      traffic_volume: trafficVolume === "" ? null : Number(trafficVolume),
      temperature_c: temperature === "" ? null : Number(temperature),
      rainfall_mm: rainfall === "" ? null : Number(rainfall),
    };
    try {
      setResult(await predictTraffic(payload));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="prediction-layout">
      <form className="form-panel" onSubmit={handleSubmit}>
        <div className="panel-heading">
          <div>
            <h2>Forecast inputs</h2>
            <p>One-step prediction from the latest earlier reading</p>
          </div>
        </div>
        <label className="field-label" htmlFor="road-segment">Road segment</label>
        <select id="road-segment" value={segmentId} onChange={(event) => setSegmentId(event.target.value)} required>
          {segments.map((segment) => <option key={segment.road_segment_id} value={segment.road_segment_id}>{segment.road_segment_id}</option>)}
        </select>
        <label className="field-label" htmlFor="forecast-time">Forecast time</label>
        <input id="forecast-time" type="datetime-local" value={forecastTimestamp} onChange={(event) => setForecastTimestamp(event.target.value)} required />
        <div className="form-rule"><span>MODEL INPUTS</span><i /></div>
        <p className="field-hint">Provide values known at forecast time. Blank values are marked in the result and handled by the model's training imputer.</p>
        <div className="form-grid">
          <div>
            <label className="field-label" htmlFor="traffic-volume">Traffic volume</label>
            <div className="input-suffix"><input id="traffic-volume" type="number" min="0" step="1" placeholder="Optional" value={trafficVolume} onChange={(event) => setTrafficVolume(event.target.value)} /><span>vehicles</span></div>
          </div>
          <div>
            <label className="field-label" htmlFor="temperature">Temperature</label>
            <div className="input-suffix"><input id="temperature" type="number" min="-80" max="70" step="0.1" placeholder="Optional" value={temperature} onChange={(event) => setTemperature(event.target.value)} /><span>°C</span></div>
          </div>
          <div>
            <label className="field-label" htmlFor="rainfall">Rainfall</label>
            <div className="input-suffix"><input id="rainfall" type="number" min="0" max="1000" step="0.1" placeholder="Optional" value={rainfall} onChange={(event) => setRainfall(event.target.value)} /><span>mm</span></div>
          </div>
        </div>
        <button className="primary-button" type="submit" disabled={loading || !segments.length}>
          {loading ? <LoaderCircle size={17} className="spin" /> : <ArrowUpRight size={17} />}
          {loading ? "Calculating" : "Generate prediction"}
        </button>
        {error && <p className="error-message" role="alert">{error}</p>}
      </form>
      <section className="result-panel" aria-live="polite">
        {result ? (
          <>
            <div className="result-kicker">MODEL OUTPUT <span>·</span> {result.forecast_horizon_hours} H AHEAD</div>
            <strong className="result-speed">{result.predicted_speed_kmh.toFixed(1)}<small> km/h</small></strong>
            <span className={`congestion-pill congestion-${result.congestion_class.toLowerCase()}`}>{result.congestion_class} congestion</span>
            <div className="result-divider" />
            <dl className="result-details">
              <div><dt>Segment</dt><dd>{result.road_segment_id}</dd></div>
              <div><dt>Forecast</dt><dd>{new Date(result.forecast_timestamp).toLocaleString()}</dd></div>
              <div><dt>Validated horizon</dt><dd>{result.validated_horizon_hours} hour</dd></div>
              <div><dt>Inputs omitted</dt><dd>{result.missing_inputs.length ? result.missing_inputs.join(", ") : "None"}</dd></div>
            </dl>
            <p className="result-notice">{result.data_notice}</p>
          </>
        ) : (
          <div className="result-empty">
            <span className="result-empty-icon"><ArrowUpRight size={21} /></span>
            <h2>Prediction result</h2>
            <p>Choose a segment and forecast time to see the estimated speed and congestion class.</p>
            <span className="result-empty-foot">PREDICTION ≠ OBSERVATION</span>
          </div>
        )}
      </section>
    </div>
  );
}
