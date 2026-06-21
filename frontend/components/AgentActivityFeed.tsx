export default function AgentActivityFeed({ trace }: any) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/5 p-4 h-[230px] overflow-y-auto">
        <h2 className="font-bold mb-3">
          AGENT ACTIVITY FEED
        </h2>
  
        <div className="space-y-3 text-sm">
          {(trace || []).length === 0 && (
            <p className="text-gray-400">
              Waiting for agent activity...
            </p>
          )}
  
          {(trace || []).map((log: any, idx: number) => (
            <div
              key={idx}
              className="rounded-lg border border-white/10 bg-black/30 p-3"
            >
              <div className="flex justify-between items-center">
                <span className="font-semibold text-cyan-400">
                  {log.agent}
                </span>
  
                <span className="text-red-400 text-xs font-mono">
                  {log.timestamp}
                </span>
              </div>
  
              <p className="mt-1 text-xs text-gray-300">
                {log.action}
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  }