'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import DagViewer from '@/components/DagViewer';

export default function RunViewerPage() {
  const params = useParams();
  const runId = (params?.id as string) || 'run_job_0001';

  const [steps, setSteps] = useState([
    { node: 'analyst', action: 'HANDOFF_SPEC', tokens: 450, latency_ms: 120, summary: 'Extracted JobSpec: PyTorch RAG' },
    { node: 'risk', action: 'AUDIT_RISK', tokens: 380, latency_ms: 110, summary: 'RiskReport: Safe=True, Score=0.05' },
    { node: 'matcher', action: 'RETRIEVE_EVIDENCE', tokens: 620, latency_ms: 160, summary: 'FitReport: Coverage=94%, 3 case studies matched' },
    { node: 'pricing', action: 'EVALUATE_PRICING', tokens: 400, latency_ms: 95, summary: 'BidDecision=BID, PriceQuote=$3,400' },
    { node: 'writer', action: 'DRAFT_PROPOSAL_ITERATION_1', tokens: 980, latency_ms: 280, summary: 'Drafted tailored opening hook & proof points' },
    { node: 'verifier', action: 'VERIFY_GROUNDING', tokens: 520, latency_ms: 130, summary: 'Claim verification: 100% grounded' },
    { node: 'critic', action: 'CRITIQUE_DRAFT', tokens: 480, latency_ms: 140, summary: 'ClientFocus=4.8/5.0, RequiresRevision=False' },
    { node: 'compliance', action: 'COMPLIANCE_GATE', tokens: 350, latency_ms: 90, summary: 'Nov 2 Policy Verified: Zero violations' },
  ]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-mono text-slate-400">Execution Telemetry</span>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Live Agent Run Viewer: {runId}</h1>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <span className="bg-slate-200 px-3 py-1 rounded font-mono font-bold">Total Tokens: 3,780 / 35,000</span>
          <span className="bg-emerald-100 text-emerald-800 px-3 py-1 rounded font-bold">Status: Awaiting Human Gate</span>
        </div>
      </div>

      <DagViewer activeNodeId="compliance" />

      {/* Execution Step Log */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Sequential Node Trace Log</h3>
        <div className="space-y-2 font-mono text-xs">
          {steps.map((s, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-slate-50 rounded border border-slate-200">
              <div className="flex items-center space-x-3">
                <span className="font-bold text-slate-400">#{idx + 1}</span>
                <span className="font-bold text-emerald-700 uppercase">[{s.node}]</span>
                <span className="text-slate-800">{s.summary}</span>
              </div>
              <div className="flex items-center space-x-4 text-slate-400 text-[11px]">
                <span>{s.tokens} tokens</span>
                <span>{s.latency_ms} ms</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

