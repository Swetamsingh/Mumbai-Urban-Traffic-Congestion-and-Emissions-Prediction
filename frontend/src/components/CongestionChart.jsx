import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

export default function CongestionChart({ data = [], title, subtitle, xLabel = "label" }) {
  return (
    <section className="chart-panel">
      <div className="panel-heading">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <span className="chart-unit">KM/H</span>
      </div>
      {data.length ? (
        <div className="chart-wrap">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 12, right: 14, bottom: 2, left: -12 }}>
              <CartesianGrid stroke="#e8eeeb" strokeDasharray="3 5" vertical={false} />
              <XAxis dataKey={xLabel} axisLine={false} tickLine={false} tick={{ fill: "#788681", fontSize: 11 }} dy={8} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: "#788681", fontSize: 11 }} width={42} />
              <Tooltip
                contentStyle={{ border: "1px solid #dfe7e2", borderRadius: 8, boxShadow: "0 8px 28px #12251e12" }}
                formatter={(value) => [`${Number(value).toFixed(1)} km/h`, "Mean speed"]}
              />
              <Line type="monotone" dataKey="mean_speed_kmh" stroke="#137a65" strokeWidth={2.5} dot={{ r: 2.5, fill: "#137a65", strokeWidth: 0 }} activeDot={{ r: 5, stroke: "#fff", strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="empty-chart">No observations are available for this selection.</div>
      )}
    </section>
  );
}
