'use client';

import React from 'react';

interface DagNode {
  id: string;
  label: string;
  type: string;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'HALTED';
}

interface DagViewerProps {
  activeNodeId?: string;
}

export default function DagViewer({ activeNodeId = 'compliance' }: DagViewerProps) {
  const nodes: DagNode[] = [
    { id: 'analyst', label: '1. Analyst', type: 'agent', status: 'COMPLETED' },
    { id: 'risk', label: '2. Risk Assessor', type: 'agent', status: 'COMPLETED' },
    { id: 'matcher', label: '3. Fit Matcher', type: 'agent', status: 'COMPLETED' },
    { id: 'pricing', label: '4. Pricing Gate', type: 'gate', status: 'COMPLETED' },
    { id: 'writer', label: '5. Writer', type: 'agent', status: 'COMPLETED' },
    { id: 'verifier', label: '6. Claim Verifier', type: 'safety', status: 'COMPLETED' },
    { id: 'critic', label: '7. Critic Loop', type: 'feedback', status: 'COMPLETED' },
    { id: 'compliance', label: '8. Compliance', type: 'safety', status: 'RUNNING' },
    { id: 'human_approval', label: '9. Human Gate', type: 'gate', status: 'PENDING' },
    { id: 'submit_live', label: '10. Submit Live', type: 'action', status: 'PENDING' },
  ];

  return (
    <div className="bg-slate-900 text-slate-100 p-6 rounded-xl border border-slate-800 shadow-md">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <h3 className="text-sm font-bold tracking-tight text-emerald-400">LangGraph Execution DAG Topology</h3>
        <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">Durable StateGraph</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {nodes.map((n) => {
          const isActive = n.id === activeNodeId;
          return (
            <div
              key={n.id}
              className={`p-3 rounded-lg border text-xs transition-all ${
                isActive
                  ? 'border-emerald-500 bg-emerald-950/40 text-emerald-300 ring-2 ring-emerald-500/20'
                  : n.status === 'COMPLETED'
                  ? 'border-slate-700 bg-slate-800/80 text-slate-300'
                  : 'border-slate-800 bg-slate-950/40 text-slate-500'
              }`}
            >
              <div className="font-semibold">{n.label}</div>
              <div className="flex items-center justify-between mt-2 text-[10px]">
                <span className="uppercase text-slate-400">{n.type}</span>
                <span className={`font-bold ${n.status === 'COMPLETED' ? 'text-emerald-400' : isActive ? 'text-amber-400' : 'text-slate-500'}`}>
                  {isActive ? 'ACTIVE' : n.status}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
