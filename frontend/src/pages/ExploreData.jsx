import { useEffect, useState } from "react";
import { getSegments, getTrends } from "../api/trafficApi.js";
import CongestionChart from "../components/CongestionChart.jsx";
import DataSourceNote from "../components/DataSourceNote.jsx";
import RoadSegmentComparison from "../components/RoadSegmentComparison.jsx";

export default function ExploreData() {
  const [segments, setSegments] = useState([]);
  const [segmentId, setSegmentId] = useState("");
  const [trends, setTrends] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getSegments()
      .then((items) => {
        setSegments(items);
        setSegmentId((current) => current || "all");
      })
      .catch((requestError) => setError(requestError.message));
  }, []);

  useEffect(() => {
    if (!segmentId) return;
    getTrends(segmentId === "all" ? undefined : segmentId)
      .then(setTrends)
      .catch((requestError) => setError(requestError.message));
  }, [segmentId]);

  return (
    <div className="page-content">
      <div className="page-heading-row">
        <div><div className="eyebrow"><span className="eyebrow-dot" /> HISTORICAL DATA</div><h1>Explore traffic patterns</h1><p className="page-description">Compare observed speeds by hour, weekday, and available road-segment ID.</p></div>
        <label className="segment-filter"><span>SEGMENT</span><select value={segmentId} onChange={(event) => setSegmentId(event.target.value)}><option value="all">All segments</option>{segments.map((segment) => <option key={segment.road_segment_id} value={segment.road_segment_id}>{segment.road_segment_id}</option>)}</select></label>
      </div>
      <DataSourceNote compact />
      {error && <div className="error-banner" role="alert">{error}</div>}
      {!trends ? <div className="loading-block">Loading traffic patterns…</div> : (
        <>
          <div className="explore-charts">
            <CongestionChart data={trends.hourly} title="Hourly profile" subtitle={segmentId === "all" ? "All represented segments" : segmentId} />
            <CongestionChart data={trends.weekdays} title="Weekday profile" subtitle="Available weekdays only" />
          </div>
          {segmentId === "all" && <RoadSegmentComparison segments={segments} />}
          <p className="footnote">No locations are geocoded in this sample; ROAD IDs must not be interpreted as named Mumbai corridors.</p>
        </>
      )}
    </div>
  );
}
