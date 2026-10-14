import { useEffect, useState } from "react";
import { getHealth } from "./api/trafficApi.js";
import Navbar from "./components/Navbar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import ExploreData from "./pages/ExploreData.jsx";
import ModelPerformance from "./pages/ModelPerformance.jsx";
import PredictTraffic from "./pages/PredictTraffic.jsx";

const pageTitles = {
  dashboard: "Overview",
  explore: "Explore data",
  predict: "Predict traffic",
  performance: "Model performance",
};

export default function App() {
  const [activePage, setActivePage] = useState("dashboard");
  const [apiConnected, setApiConnected] = useState(false);

  useEffect(() => {
    getHealth().then(() => setApiConnected(true)).catch(() => setApiConnected(false));
  }, []);

  return (
    <div className="app-shell">
      <Navbar activePage={activePage} onNavigate={setActivePage} apiConnected={apiConnected} />
      <main className="main-shell">
        <header className="topbar">
          <div className="breadcrumb"><span>Cityflow</span><i>/</i><strong>{pageTitles[activePage]}</strong></div>
          <div className="region-label"><span className="region-mark" /> Mumbai urban region <span className="region-state">MAHARASHTRA, INDIA</span></div>
        </header>
        {activePage === "dashboard" && <Dashboard onNavigate={setActivePage} />}
        {activePage === "explore" && <ExploreData />}
        {activePage === "predict" && <PredictTraffic />}
        {activePage === "performance" && <ModelPerformance />}
      </main>
    </div>
  );
}
