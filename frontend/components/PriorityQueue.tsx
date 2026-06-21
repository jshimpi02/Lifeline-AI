export default function PriorityQueue({ clusters }: any) {
    const ranked = [...clusters].sort(
      (a, b) => b.priority_score - a.priority_score
    );
  
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[230px] overflow-y-auto">
        <h2 className="font-bold mb-3">PRIORITY QUEUE</h2>
        <div className="space-y-2">
          {ranked.map((c: any, i: number) => (
            <div key={c.cluster_id} className="flex justify-between rounded bg-black/30 p-2 text-sm">
              <span>
                {i + 1}. {c.summary.slice(0, 40)}
              </span>
              <span className="text-red-400 font-bold">{c.priority_score}</span>
            </div>
          ))}
        </div>
      </div>
    );
  }