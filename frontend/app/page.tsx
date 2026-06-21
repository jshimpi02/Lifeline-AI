"use client";

import { useEffect, useState } from "react";
import {
  getMapClusters,
  getMapEvents,
  processReport,
  getAgentLogs,
} from "@/lib/api";

import LiveFeed from "@/components/LiveFeed";
import IncidentMap from "@/components/IncidentMap";
import IncidentDetails from "@/components/IncidentDetails";
import AgentActivityFeed from "@/components/AgentActivityFeed";
import PriorityQueue from "@/components/PriorityQueue";

export default function Home() {
  const [criticalCluster, setCriticalCluster] = useState<any | null>(null);
  const [clusters, setClusters] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [selectedCluster, setSelectedCluster] = useState<any | null>(null);
  const [feed, setFeed] = useState<any[]>([]);
  const [notification, setNotification] = useState<string | null>(null);
  const [agentLogs, setAgentLogs] = useState<any[]>([]);

  async function refresh() {
    try {
      const [c, e, logs] = await Promise.all([
        getMapClusters(),
        getMapEvents(),
        getAgentLogs(),
      ]);

      setClusters(Array.isArray(c) ? c : []);
      setEvents(Array.isArray(e) ? e : []);
      setAgentLogs(Array.isArray(logs) ? logs : []);

      const ranked = Array.isArray(c)
        ? [...c].sort((a, b) => b.priority_score - a.priority_score)
        : [];

      if (ranked.length > 0) {
        setSelectedCluster(ranked[0]);
      }

      const critical = ranked.find((cluster) => cluster.priority_score >= 85);

      if (critical) {
        setCriticalCluster(critical);
      }
    } catch (err) {
      console.error("refresh failed:", err);
    }
  }

  async function submitReport(text: string, source = "field") {
    const result = await processReport(text, source);

    setFeed((prev) => [
      {
        source,
        text,
        time: new Date().toLocaleTimeString(),
        result,
      },
      ...prev,
    ]);

    const fusionTool = result.tool_calls_executed?.find(
      (t: any) => t.tool === "submit_to_fusion"
    );

    const cluster = fusionTool?.result?.cluster;

    if (cluster) {
      setNotification(
        `${cluster.summary} | Priority ${cluster.priority_score}`
      );
      setSelectedCluster(cluster);
    }

    await refresh();
  }

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-[#070b12] text-white">
      <div className="border-b border-white/10 px-6 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">LIFELINE AI</h1>
          <p className="text-sm text-gray-400">
            AI-Powered Disaster Response
          </p>
        </div>

        <div className="text-green-400 text-sm">● SYSTEM OPERATIONAL</div>
      </div>

      {criticalCluster && (
        <div className="mx-6 mt-4 rounded-xl border border-red-500/60 bg-red-500/15 px-5 py-4 shadow-lg">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-bold text-red-300">
                🚨 CRITICAL INCIDENT DETECTED
              </p>

              <h2 className="mt-1 text-lg font-bold">
                {criticalCluster.summary}
              </h2>

              <p className="mt-1 text-sm text-gray-300">
                Priority: {criticalCluster.priority_score} • Confidence:{" "}
                {criticalCluster.confidence} • Reports:{" "}
                {criticalCluster.reports_count}
              </p>
            </div>

            <div className="flex gap-2">
              <button
                onClick={() => setSelectedCluster(criticalCluster)}
                className="rounded-lg bg-white/10 px-4 py-2 text-sm hover:bg-white/20"
              >
                View Incident
              </button>

              <button
                onClick={() => setCriticalCluster(null)}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-bold hover:bg-red-700"
              >
                Acknowledge
              </button>
            </div>
          </div>
        </div>
      )}

      {notification && (
        <div className="mx-6 mt-4 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3">
          🚨 High Priority Update: {notification}
        </div>
      )}

      <div className="grid grid-cols-12 gap-4 p-6">
        <section className="col-span-3">
          <LiveFeed feed={feed} onSubmitReport={submitReport} />
        </section>

        <section className="col-span-6 space-y-4">
          <IncidentMap
            clusters={clusters}
            events={events}
            onSelectCluster={setSelectedCluster}
          />

          <div className="grid grid-cols-2 gap-4">
            <PriorityQueue clusters={clusters} />

            <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[230px]">
              <h2 className="font-bold mb-3">SYSTEM INTELLIGENCE</h2>

              <div className="space-y-2 text-sm text-gray-300">
                <p>✅ ASI:One selecting and calling tools</p>
                <p>✅ Browserbase watching web/weather sources</p>
                <p>✅ Fusion Engine merging related reports</p>
                <p>✅ Memory Agent retrieving historical incidents</p>
                <p>✅ Priority engine ranking active clusters</p>
              </div>
            </div>
          </div>
        </section>

        <section className="col-span-3 space-y-4">
          <IncidentDetails cluster={selectedCluster} />
          <AgentActivityFeed trace={agentLogs} />
        </section>
      </div>
    </main>
  );
}