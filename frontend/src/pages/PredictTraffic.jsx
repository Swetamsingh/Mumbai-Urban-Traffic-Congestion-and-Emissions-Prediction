import { useEffect, useState } from "react";
import { getSegments, getSummary } from "../api/trafficApi.js";
import DataSourceNote from "../components/DataSourceNote.jsx";
import TrafficPredictionForm from "../components/TrafficPredictionForm.jsx";

export default function PredictTraffic() {
  const [segments, setSegments] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getSegments(), getSummary()])
      .then(([roadSegments, datasetSummary]) => {
        setSegments(roadSegments);
        setSummary(datasetSummary);
      })
      .catch((requestError) => setError(requestError.message));
  }, []);

  return (
    <div className="page-content">
      <div className="page-heading-row">
        <div><div className="eyebrow"><span className="eyebrow-dot" /> ONE-STEP MODEL OUTPUT</div><h1>Predict traffic speed</h1><p className="page-description">A Random Forest estimate for the selected segment and next forecast interval.</p></div>
        <span className="horizon-badge">VALIDATED HORIZON <strong>1 hour</strong></span>
      </div>
      <DataSourceNote compact />
      {error && <div className="error-banner" role="alert">{error}</div>}
      {!summary ? <div className="loading-block">Preparing prediction inputs…</div> : <TrafficPredictionForm segments={segments} summary={summary} />}
      <p className="footnote">Longer forecast horizons are not validated. Optional volume and weather values are not fabricated; omitted inputs are disclosed in the result.</p>
    </div>
  );
}
