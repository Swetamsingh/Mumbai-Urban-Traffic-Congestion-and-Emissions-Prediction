const API_BASE = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new Error("Cannot reach the API. Start the FastAPI server on port 8000.");
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = payload.detail;
    throw new Error(typeof detail === "string" ? detail : `Request failed (${response.status}).`);
  }
  return payload;
}

export const getHealth = () => request("/health");
export const getSummary = () => request("/api/summary");
export const getSegments = () => request("/api/segments");
export const getTrends = (segmentId) => {
  const query = segmentId ? `?segment_id=${encodeURIComponent(segmentId)}` : "";
  return request(`/api/trends${query}`);
};
export const getModelMetrics = () => request("/api/model-metrics");

export const predictTraffic = (payload) =>
  request("/api/predict", { method: "POST", body: JSON.stringify(payload) });

export const estimateEmissions = (payload) =>
  request("/api/emissions/estimate", { method: "POST", body: JSON.stringify(payload) });
