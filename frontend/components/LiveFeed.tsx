"use client";

import { useState } from "react";

export default function LiveFeed({ feed, onSubmitReport }: any) {
  const [text, setText] = useState("");
  const [running, setRunning] = useState(false);

  const weatherReports = [
    "Weather agent reports rainfall in San Francisco with possible flood risk near low-lying roads and intersections.",
    "Weather agent reports strong winds in San Francisco. Potential risk for traffic disruption and power outages.",
    "Weather alert: precipitation probability increasing across San Francisco. Emergency teams should monitor flood-prone areas.",
    "Weather intelligence update: road conditions may worsen near Market Street and Mission Street due to rainfall.",
  ];

  async function startWeatherFeed() {
    if (running) return;
    setRunning(true);

    for (const report of weatherReports) {
      await onSubmitReport(report, "weather");
      await new Promise((resolve) => setTimeout(resolve, 2500));
    }

    setRunning(false);
  }

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[820px] overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-bold">LIVE WEATHER INTELLIGENCE</h2>
        <span className="rounded bg-blue-500 px-2 py-1 text-xs">WEATHER</span>
      </div>

      <button
        onClick={startWeatherFeed}
        disabled={running}
        className="mb-4 w-full rounded-lg bg-blue-600 hover:bg-blue-700 px-3 py-2 text-sm disabled:opacity-50"
      >
        {running ? "Weather Feed Running..." : "Start Weather Feed"}
      </button>

      <div className="space-y-2 mb-4">
        {weatherReports.map((report) => (
          <button
            key={report}
            onClick={() => onSubmitReport(report, "weather")}
            className="w-full rounded-lg bg-blue-500/20 hover:bg-blue-500/30 px-3 py-2 text-left text-sm"
          >
            Push weather report
            <p className="text-gray-300">{report}</p>
          </button>
        ))}
      </div>

      <div className="flex gap-2 mb-4">
        <input
          className="flex-1 rounded bg-black/40 border border-white/10 px-3 py-2 text-sm"
          placeholder="Type weather/intel report..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button
          className="rounded bg-blue-500 px-3 py-2 text-sm"
          onClick={() => {
            if (!text.trim()) return;
            onSubmitReport(text, "weather");
            setText("");
          }}
        >
          Send
        </button>
      </div>

      <div className="space-y-3">
        {feed.map((item: any, idx: number) => (
          <div
            key={idx}
            className="rounded-lg bg-black/30 border border-white/10 p-3"
          >
            <div className="flex justify-between text-xs text-gray-400">
              <span className="uppercase text-blue-400">{item.source}</span>
              <span>{item.time}</span>
            </div>

            <p className="mt-2 text-sm">{item.text}</p>

            <div className="mt-2 text-xs text-blue-300">
              <p>ASI:One Tool Orchestration</p>
              <p className="text-white/80">
                Tools called:{" "}
                {item.result?.tool_calls_executed
                  ?.map((t: any) => t.tool)
                  .join(" → ")}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}