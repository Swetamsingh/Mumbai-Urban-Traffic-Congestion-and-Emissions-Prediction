import { useEffect, useState } from "react";
import { ArrowUpRight, CalendarDays, Database, MapPin } from "lucide-react";
import { getSegments, getSummary, getTrends } from "../api/trafficApi.js";
import CongestionChart from "../components/CongestionChart.jsx";
import DataSourceNote from "../components/DataSourceNote.jsx";
import EmissionsPanel from "../components/EmissionsPanel.jsx";
import RoadSegmentComparison from "../components/RoadSegmentComparison.jsx";
import SummaryCards from "../components/SummaryCards.jsx";

function formatDate(value) {
  return value ? new Date(value).toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" }) : "—";
}

export default function Dashboard({ onNavigate }) {
  const [summary, setSummary] = useState(null);
  const [segments, setSegments] = useState([]);
  const [trends, setTrends] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getSummary(), getSegments(), getTrends()])
      .then(([datasetSummary, roadSegments, trafficTrends]) => {
        setSummary(datasetSummary);
        setSegments(roadSegments);
        setTrends(trafficTrends);
      })
      .catch((requestError) => setError(requestError.message));
  }, []);

  return (
    <div className="page-content">
      <div className="page-heading-row">
        <div>
          <div className="eyebrow"><span className="eyebrow-dot" /> STUDY REGION / MUMBAI URBAN REGION</div>
          <h1>Traffic at a glance</h1>
          <p className="page-description">Historical speed patterns and model-backed estimates for the current demonstration dataset.</p>
        </div>
        <button className="text-action" type="button" onClick={() => onNavigate("explore")}>Explore patterns <ArrowUpRight size={16} /></button>
      </div>
      <DataSourceNote compact />
      {error && <div className="error-banner" role="alert">{error}</div>}
      {!summary ? <div className="loading-block">Loading dataset coverage…</div> : (
        <>
          <SummaryCards summary={summary} />
          <section className="coverage-strip">
            <div className="coverage-item"><MapPin size={16} /><div><small>Study region</small><strong>{summary.region}</strong></div></div>
            <div className="coverage-item"><CalendarDays size={16} /><div><small>Sample time range</small><strong>{formatDate(summary.coverage_start)} — {formatDate(summary.coverage_end)}</strong></div></div>
            <div className="coverage-item"><Database size={16} /><div><small>Dataset</small><strong>{summary.dataset_name}</strong></div></div>
          </section>
          <div className="section-divider"><span>OBSERVED PATTERNS</span><i /></div>
          <div className="dashboard-chart-grid">
            <CongestionChart data={trends?.hourly} title="Speed by hour" subtitle="Average observed speed across available segments" />
            <RoadSegmentComparison segments={segments} />
          </div>
          <div className="dashboard-lower-grid">
            <CongestionChart data={trends?.weekdays} title="Speed by weekday" subtitle="Only weekdays represented in the sample appear" />
            <section className="next-step-panel">
              <span className="next-step-index">01 / PREDICT</span>
              <h2>Look one interval ahead</h2>
              <p>Choose a segment and forecast time. The API uses only earlier segment readings for lag context.</p>
              <button className="outline-button" type="button" onClick={() => onNavigate("predict")}>Open prediction <ArrowUpRight size={15} /></button>
            </section>
          </div>
          <div className="section-divider"><span>DERIVED EMISSIONS ESTIMATE</span><i /></div>
          <EmissionsPanel />
        </>
      )}
    </div>
  );
}
