'use client';

import React, { useState, useEffect } from 'react';

interface DegradedModeBannerProps {
  forcedDegraded?: boolean;
}

export default function DegradedModeBanner({ forcedDegraded = false }: DegradedModeBannerProps) {
  const [isDegraded, setIsDegraded] = useState(forcedDegraded);

  useEffect(() => {
    if (forcedDegraded) {
      setIsDegraded(true);
      return;
    }
    // Check API health status
    fetch('http://localhost:8000/health')
      .then((res) => {
        if (!res.ok) setIsDegraded(true);
        else setIsDegraded(false);
      })
      .catch(() => setIsDegraded(true));
  }, [forcedDegraded]);

  if (!isDegraded) return null;

  return (
    <div
      data-testid="degraded-mode-banner"
      className="bg-amber-500 text-slate-900 px-4 py-2 text-sm font-semibold flex items-center justify-between shadow-md"
    >
      <div className="flex items-center space-x-2">
        <span className="bg-amber-700 text-white rounded-full px-2 py-0.5 text-xs uppercase tracking-wider font-bold">
          Degraded Mode
        </span>
        <span>
          Marketplace MCP or external backend disconnected. Submissions are queued safely with zero connects spent.
        </span>
      </div>
      <button
        onClick={() => setIsDegraded(false)}
        className="text-amber-950 hover:text-black font-bold text-xs underline"
      >
        Dismiss
      </button>
    </div>
  );
}
