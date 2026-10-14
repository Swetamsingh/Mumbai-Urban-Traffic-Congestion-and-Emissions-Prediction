import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function RoadSegmentComparison({ segments = [] }) {
  const data = segments.map((segment) => ({
    road_segment_id: segment.road_segment_id,
    mean_speed_kmh: Number(segment.mean_speed_kmh),
    observation_count: segment.observation_count,
  }));
  return (
    <section className="chart-panel comparison-panel">
      <div className="panel-heading">
        <div>
          <h2>Segment comparison</h2>
          <p>Mean observed speed by dataset ID</p>
        </div>
        <span className="chart-unit">KM/H</span>
      </div>
      {data.length ? (
        <div className="chart-wrap comparison-chart">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 14, bottom: 2, left: -12 }}>
              <CartesianGrid stroke="#e8eeeb" strokeDasharray="3 5" vertical={false} />
              <XAxis dataKey="road_segment_id" axisLine={false} tickLine={false} tick={{ fill: "#788681", fontSize: 11 }} dy={8} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: "#788681", fontSize: 11 }} width={42} />
              <Tooltip
                contentStyle={{ border: "1px solid #dfe7e2", borderRadius: 8 }}
                formatter={(value, _name, item) => [`${Number(value).toFixed(1)} km/h`, `${item.payload.observation_count} observations`]}
              />
              <Bar dataKey="mean_speed_kmh" fill="#e17b51" radius={[4, 4, 0, 0]} maxBarSize={48} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="empty-chart">No road segments were returned by the API.</div>
      )}
    </section>
  );
}
