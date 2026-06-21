import axios from "axios";

export const api = axios.create({
  baseURL: "/api",
});

export async function getMapClusters() {
  const res = await api.get("/map/clusters");
  return res.data;
}

export async function getMapEvents() {
  const res = await api.get("/map/events");
  return res.data;
}

export async function processReport(raw_text: string, source = "field") {
    const res = await api.post("/agent/asi-process-report", {
    raw_text,
    source,
  });
  return res.data;
}

export async function getClusterExplain(clusterId: string) {
  const res = await api.get(`/clusters/${clusterId}/explain`);
  return res.data;
}

export async function getSimilarHistory(clusterId: string) {
  const res = await api.get(`/clusters/${clusterId}/similar-history`);
  return res.data;
}
export async function getAgentLogs() {
    const res = await api.get("/agent/logs");
    return res.data;
  }
