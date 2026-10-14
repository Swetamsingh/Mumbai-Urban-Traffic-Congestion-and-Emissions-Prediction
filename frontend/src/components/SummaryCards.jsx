import { Activity, Gauge, Map, Waves } from "lucide-react";

function formatNumber(value, digits = 1) {
  return Number.isFinite(Number(value))
    ? Number(value).toLocaleString(undefined, { maximumFractionDigits: digits })
    : "—";
}

export default function SummaryCards({ summary }) {
  const cards = [
    { label: "Observations", value: formatNumber(summary.row_count, 0), detail: "hourly sample rows", icon: Activity, tone: "green" },
    { label: "Road segments", value: formatNumber(summary.segment_count, 0), detail: "IDs in this dataset", icon: Map, tone: "blue" },
    { label: "Mean speed", value: `${formatNumber(summary.mean_speed_kmh)} km/h`, detail: "across observations", icon: Gauge, tone: "orange" },
    { label: "Median speed", value: `${formatNumber(summary.median_speed_kmh)} km/h`, detail: "across observations", icon: Waves, tone: "violet" },
  ];

  return (
    <div className="summary-grid">
      {cards.map(({ label, value, detail, icon: Icon, tone }) => (
        <article className="summary-card" key={label}>
          <div className={`summary-icon tone-${tone}`}><Icon size={18} /></div>
          <div className="summary-copy">
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{detail}</small>
          </div>
        </article>
      ))}
    </div>
  );
}
