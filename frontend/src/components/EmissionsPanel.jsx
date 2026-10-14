import { useState } from "react";
import { ArrowRight, LoaderCircle } from "lucide-react";
import { estimateEmissions } from "../api/trafficApi.js";

export default function EmissionsPanel() {
  const [vehicleCount, setVehicleCount] = useState("500");
  const [segmentLength, setSegmentLength] = useState("2");
  const [factor, setFactor] = useState("180");
  const [period, setPeriod] = useState("per hour");
  const [source, setSource] = useState("Illustrative prototype factor; not locally sourced");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      setResult(await estimateEmissions({
        vehicle_count: Number(vehicleCount),
        segment_length_km: Number(segmentLength),
        emission_factor_g_per_vehicle_km: Number(factor),
        observation_period: period,
        emission_factor_source: source,
      }));
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="emissions-layout">
      <form className="form-panel emissions-form" onSubmit={handleSubmit}>
        <div className="panel-heading"><div><h2>Estimate by vehicle-kilometres</h2><p>Independent of the traffic-speed prediction</p></div></div>
        <div className="form-grid">
          <div><label className="field-label" htmlFor="vehicle-count">Vehicle count</label><input id="vehicle-count" type="number" min="0" step="1" required value={vehicleCount} onChange={(event) => setVehicleCount(event.target.value)} /></div>
          <div><label className="field-label" htmlFor="period">Count period</label><select id="period" value={period} onChange={(event) => setPeriod(event.target.value)}><option>per hour</option><option>per 15 minutes</option><option>per day</option><option>custom interval</option></select></div>
          <div><label className="field-label" htmlFor="segment-length">Segment length</label><div className="input-suffix"><input id="segment-length" type="number" min="0.1" step="0.1" required value={segmentLength} onChange={(event) => setSegmentLength(event.target.value)} /><span>km</span></div></div>
          <div><label className="field-label" htmlFor="emission-factor">Emission factor</label><div className="input-suffix"><input id="emission-factor" type="number" min="1" step="1" required value={factor} onChange={(event) => setFactor(event.target.value)} /><span>g / veh-km</span></div></div>
          <div className="source-field"><label className="field-label" htmlFor="factor-source">Factor source</label><input id="factor-source" type="text" maxLength="300" required value={source} onChange={(event) => setSource(event.target.value)} /></div>
        </div>
        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? <LoaderCircle size={17} className="spin" /> : <ArrowRight size={17} />}
          {loading ? "Estimating" : "Calculate estimate"}
        </button>
        {error && <p className="error-message" role="alert">{error}</p>}
      </form>
      <section className="emissions-result" aria-live="polite">
        {result ? (
          <>
            <span className="result-kicker">DERIVED CO₂ ESTIMATE · {result.observation_period.toUpperCase()}</span>
            <strong>{result.co2_kg.toLocaleString(undefined, { maximumFractionDigits: 2 })}<small> kg</small></strong>
            <span className="emissions-grams">{result.co2_grams.toLocaleString(undefined, { maximumFractionDigits: 1 })} grams CO₂</span>
            <dl className="result-details">
              <div><dt>Vehicle-kilometres</dt><dd>{result.vehicle_km.toLocaleString()}</dd></div>
              <div><dt>Factor</dt><dd>{result.emission_factor_g_per_vehicle_km} g / vehicle-km</dd></div>
              <div><dt>Source</dt><dd>{result.emission_factor_source}</dd></div>
            </dl>
            <p className="result-notice">{result.assumption}</p>
          </>
        ) : (
          <div className="result-empty"><span className="result-empty-foot">CALCULATION</span><h2>Estimated CO₂</h2><p>Enter a count, distance, and factor to calculate a derived estimate.</p></div>
        )}
      </section>
    </div>
  );
}
