import { AlertTriangle } from "lucide-react";

export default function DataSourceNote({ compact = false }) {
  return (
    <aside className={`source-note ${compact ? "source-note-compact" : ""}`} role="note">
      <AlertTriangle size={17} aria-hidden="true" />
      <div>
        <strong>Synthetic demonstration data</strong>
        <p>
          The sample contains illustrative road IDs only. It is not measured Mumbai traffic and does not validate model performance for Mumbai.
        </p>
      </div>
    </aside>
  );
}
