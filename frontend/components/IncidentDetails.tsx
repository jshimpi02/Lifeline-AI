"use client";

import { useEffect, useState } from "react";
import { getClusterExplain, getSimilarHistory } from "@/lib/api";

export default function IncidentDetails({ cluster }: any) {
  const [explain, setExplain] = useState<any>(null);
  const [history, setHistory] = useState<any>(null);
  const [tab, setTab] = useState("summary");
  const [dispatched, setDispatched] = useState(false);

  useEffect(() => {
    async function load() {
      if (!cluster?.cluster_id) return;

      setDispatched(false);
      setTab("summary");

      const [explainRes, historyRes] = await Promise.all([
        getClusterExplain(cluster.cluster_id),
        getSimilarHistory(cluster.cluster_id),
      ]);

      setExplain(explainRes);
      setHistory(historyRes);
    }

    load();
  }, [cluster]);

  if (!cluster) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[430px]">
        <h2 className="font-bold">INCIDENT DETAILS</h2>
        <p className="text-gray-400 mt-4">Select a cluster on the map.</p>
      </div>
    );
  }

  const priorityLabel =
    cluster.priority_score >= 85
      ? "CRITICAL"
      : cluster.priority_score >= 70
      ? "HIGH"
      : cluster.priority_score >= 50
      ? "MEDIUM"
      : "LOW";

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[520px] overflow-y-auto">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h2 className="font-bold">INCIDENT DETAILS</h2>
          <h3 className="mt-3 text-lg font-bold text-red-400">
            {cluster.event_type?.replace("_", " ").toUpperCase()} CLUSTER
          </h3>
        </div>

        <span className="rounded bg-red-500 px-2 py-1 text-xs font-bold">
          {priorityLabel}
        </span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
        <p className="text-gray-400">Location</p>
        <p className="text-right">{cluster.summary?.split("near ")[1] || "Unknown"}</p>

        <p className="text-gray-400">Priority Score</p>
        <p className="text-right text-red-400 font-bold">
          {cluster.priority_score} / 100
        </p>

        <p className="text-gray-400">Reports Fused</p>
        <p className="text-right">{cluster.reports_count}</p>

        <p className="text-gray-400">Confidence</p>
        <p className="text-right">{cluster.confidence}</p>

        <p className="text-gray-400">Severity</p>
        <p className="text-right">{cluster.severity}</p>
      </div>

      <div className="mt-5 flex gap-2 border-b border-white/10 pb-2 text-xs">
        {["summary", "explanation", "memory", "recommendation"].map((name) => (
          <button
            key={name}
            onClick={() => setTab(name)}
            className={`uppercase ${
              tab === name ? "text-red-400" : "text-gray-400"
            }`}
          >
            {name}
          </button>
        ))}
      </div>

      <div className="mt-4 min-h-[150px] text-sm text-gray-300">
        {tab === "summary" && (
          <div className="space-y-3">
            <p>{cluster.summary}</p>
            <p>
              <span className="text-gray-500">Event Type:</span>{" "}
              {cluster.event_type}
            </p>
            <p>
              <span className="text-gray-500">Recommended Action:</span>{" "}
              {cluster.recommended_action}
            </p>
          </div>
        )}

        {tab === "explanation" && (
          <ul className="list-disc pl-5 space-y-2">
            {explain?.reasoning?.length ? (
              explain.reasoning.map((r: string) => <li key={r}>{r}</li>)
            ) : (
              <li>No explanation available.</li>
            )}
          </ul>
        )}

        {tab === "memory" && (
          <div className="space-y-3">
            {history?.historical_event ? (
              <>
                <p>
                  <span className="text-gray-500">Similar Event:</span>{" "}
                  {history.historical_event.title}
                </p>
                <p>
                  <span className="text-gray-500">Similarity:</span>{" "}
                  {history.similarity_score}
                </p>
                <p>{history.memory_insight}</p>
              </>
            ) : (
              <p>No similar historical memory found.</p>
            )}
          </div>
        )}

        {tab === "recommendation" && (
          <div className="space-y-3">
            <p className="text-white font-semibold">
              {cluster.recommended_action}
            </p>
            <p>
              Suggested next step: assign response unit, monitor cluster growth,
              and update status once field team confirms arrival.
            </p>
          </div>
        )}
      </div>

      <button
        onClick={() => setDispatched(true)}
        className={`mt-4 w-full rounded-lg px-4 py-3 font-bold ${
          dispatched
            ? "bg-green-600 text-white"
            : "bg-red-600 hover:bg-red-700 text-white"
        }`}
      >
        {dispatched ? "✓ Marked as Dispatched" : "🚑 Mark as Dispatched"}
      </button>
    </div>
  );
}