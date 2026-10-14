import {
  Activity,
  ChartNoAxesCombined,
  CircleGauge,
  LayoutDashboard,
  MapPinned,
} from "lucide-react";

const links = [
  { id: "dashboard", label: "Overview", icon: LayoutDashboard },
  { id: "explore", label: "Explore data", icon: ChartNoAxesCombined },
  { id: "predict", label: "Predict traffic", icon: CircleGauge },
  { id: "performance", label: "Model performance", icon: Activity },
];

export default function Navbar({ activePage, onNavigate, apiConnected }) {
  return (
    <aside className="sidebar">
      <a className="brand" href="#dashboard" onClick={() => onNavigate("dashboard")}>
        <span className="brand-mark"><MapPinned size={19} strokeWidth={2.1} /></span>
        <span className="brand-copy">
          <strong>Cityflow</strong>
          <small>TRAFFIC INTELLIGENCE</small>
        </span>
      </a>
      <div className="sidebar-section-label">WORKSPACE</div>
      <nav className="primary-nav" aria-label="Main navigation">
        {links.map(({ id, label, icon: Icon }) => (
          <button
            className={`nav-item ${activePage === id ? "is-active" : ""}`}
            key={id}
            onClick={() => onNavigate(id)}
            type="button"
          >
            <Icon size={17} strokeWidth={1.9} />
            <span>{label}</span>
          </button>
        ))}
      </nav>
      <div className="sidebar-bottom">
        <div className={`api-status ${apiConnected ? "is-online" : "is-offline"}`}>
          <span className="status-dot" />
          <span>{apiConnected ? "API connected" : "API unavailable"}</span>
        </div>
        <p>Prototype dataset<br />Not live traffic</p>
      </div>
    </aside>
  );
}
