"use client";

import { useEffect, useState } from "react";

function getColor(priority: number) {
  if (priority >= 85) return "bg-red-500 border-red-300";
  if (priority >= 70) return "bg-orange-500 border-orange-300";
  if (priority >= 50) return "bg-yellow-500 border-yellow-300";
  return "bg-blue-500 border-blue-300";
}

function getSize(reports: number) {
  if (reports >= 5) return "w-24 h-24";
  if (reports >= 3) return "w-20 h-20";
  return "w-16 h-16";
}

export default function MapInner({ onSelectCluster }: any) {
  const [clusters, setClusters] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);

  async function loadMapData() {
    try {
      const [clusterRes, eventRes] = await Promise.all([
        fetch("http://127.0.0.1:8000/map/clusters"),
        fetch("http://127.0.0.1:8000/map/events"),
      ]);

      const c = await clusterRes.json();
      const e = await eventRes.json();

      setClusters(Array.isArray(c) ? c : []);
      setEvents(Array.isArray(e) ? e : []);
    } catch (err) {
      console.error("Map data failed:", err);
    }
  }

  useEffect(() => {
    loadMapData();
    const interval = setInterval(loadMapData, 2000);
    return () => clearInterval(interval);
  }, []);

  const visibleClusters = clusters.filter(
    (c) => c.lat !== null && c.lng !== null
  );

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[560px]">
      <h2 className="font-bold mb-3">
        LIVE INCIDENT MAP ({visibleClusters.length} clusters, {events.length} events)
      </h2>

      <div className="relative h-[500px] w-full overflow-hidden rounded-xl bg-black">
        <iframe
          title="San Francisco Map"
          className="absolute inset-0 h-full w-full opacity-80"
          src="https://www.openstreetmap.org/export/embed.html?bbox=-122.53%2C37.70%2C-122.35%2C37.83&layer=mapnik"
        />

        {visibleClusters.map((cluster, idx) => {
          const positions = [
            "left-[45%] top-[48%]",
            "left-[55%] top-[42%]",
            "left-[38%] top-[55%]",
            "left-[62%] top-[58%]",
            "left-[50%] top-[35%]",
          ];

          const pos = positions[idx % positions.length];

          return (
            <button
              key={cluster.cluster_id}
              onClick={() => onSelectCluster(cluster)}
              className={`absolute ${pos} ${getSize(
                cluster.reports_count
              )} -translate-x-1/2 -translate-y-1/2 rounded-full border-4 ${getColor(
                cluster.priority_score
              )} bg-opacity-60 animate-pulse shadow-2xl`}
            >
              <div className="flex h-full w-full flex-col items-center justify-center text-center text-xs font-bold text-white">
                <span>{cluster.priority_score}</span>
                <span>{cluster.reports_count} reports</span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}