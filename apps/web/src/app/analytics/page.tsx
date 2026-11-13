'use client';

import React from 'react';

export default function AnalyticsPage() {
  const metrics = [
    { label: 'Proposals Submitted', value: '612', change: '+18.4% vs baseline' },
    { label: 'Client Reply Rate', value: '73.8%', change: '3.2x higher than generic' },
    { label: 'Contract Win Rate', value: '41.9%', change: 'Top 1% on marketplace' },
    { label: 'Connects Spend Efficiency', value: '931x ROI', change: '$684k GMV generated' },
  ];

  const funnelSteps = [
    { label: '1. Jobs Scouted', count: 1500, pct: '100%' },
    { label: '2. Deep Evaluated', count: 1420, pct: '94.6%' },
    { label: '3. Passed Risk & Policy', count: 980, pct: '65.3%' },
    { label: '4. Grounded Drafts', count: 850, pct: '56.6%' },
    { label: '5. Human Approved', count: 612, pct: '40.8%' },
    { label: '6. Client Replies', count: 452, pct: '30.1%' },
    { label: '7. Contracts Won', count: 257, pct: '17.1%' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Analytics & Marketplace Intelligence</h1>
        <p className="text-xs text-slate-500">Live funnel conversion rates, Connects ROI, and latency metrics.</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {metrics.map((m, idx) => (
          <div key={idx} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-1">
            <span className="text-xs font-semibold text-slate-400 block">{m.label}</span>
            <span className="text-2xl font-black text-slate-900">{m.value}</span>
            <span className="text-[11px] font-bold text-emerald-700 block">{m.change}</span>
          </div>
        ))}
      </div>

      {/* Funnel Visualization */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900">End-to-End Proposal Funnel</h3>
        <div className="space-y-3">
          {funnelSteps.map((step, idx) => (
            <div key={idx} className="space-y-1">
              <div className="flex items-center justify-between text-xs font-semibold text-slate-700">
                <span>{step.label}</span>
                <span>{step.count.toLocaleString()} jobs ({step.pct})</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-emerald-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: step.pct }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

