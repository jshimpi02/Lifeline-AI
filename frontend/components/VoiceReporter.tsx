"use client";

import { useState } from "react";

export default function VoiceReporter({ onSubmitReport }: any) {
  const [text, setText] = useState(
    "Nursing home needs evacuation, water level is increasing and power may go out soon"
  );

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[270px]">
      <h2 className="font-bold mb-3">VOICE REPORTER</h2>

      <div className="rounded bg-black/30 p-3 text-green-400 text-sm mb-3">
        Mock Deepgram transcript
      </div>

      <textarea
        className="w-full h-24 rounded bg-black/40 border border-white/10 p-3 text-sm"
        value={text}
        onChange={(e) => setText(e.target.value)}
      />

      <button
        className="mt-3 w-full rounded bg-green-600 hover:bg-green-700 px-4 py-2"
        onClick={() => onSubmitReport(text, "voice")}
      >
        Submit Voice Report
      </button>
    </div>
  );
}