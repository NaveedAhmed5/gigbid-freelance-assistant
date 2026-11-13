'use client';

import React from 'react';
import Link from 'next/link';

interface PipelineCard {
  id: string;
  jobTitle: string;
  clientName: string;
  bidAmount: number;
  stage: 'draft' | 'approval' | 'submitted' | 'replied' | 'won' | 'lost';
}

export default function KanbanBoard() {
  const cards: PipelineCard[] = [
    { id: 'job_001', jobTitle: 'Enterprise PyTorch RAG Pipeline', clientName: 'HealthTech AI', bidAmount: 3400, stage: 'approval' },
    { id: 'job_002', jobTitle: 'Next.js Distributed Dashboard', clientName: 'FinServe Corp', bidAmount: 4200, stage: 'submitted' },
    { id: 'job_003', jobTitle: 'Snowflake Analytics Pipeline', clientName: 'RetailEdge', bidAmount: 2800, stage: 'replied' },
    { id: 'job_004', jobTitle: 'Multi-Tenant OAuth Gateway', clientName: 'SaaSify Inc', bidAmount: 5100, stage: 'won' },
  ];

  const columns = [
    { key: 'draft', label: 'Drafting' },
    { key: 'approval', label: 'Pending Approval' },
    { key: 'submitted', label: 'Submitted' },
    { key: 'replied', label: 'Client Replied' },
    { key: 'won', label: 'Contract Won' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {columns.map((col) => {
        const colCards = cards.filter((c) => c.stage === col.key);
        return (
          <div key={col.key} className="bg-slate-100 rounded-lg p-3 border border-slate-200">
            <div className="flex items-center justify-between mb-3 px-1">
              <h4 className="font-bold text-xs uppercase tracking-wider text-slate-700">{col.label}</h4>
              <span className="text-xs font-semibold bg-white px-2 py-0.5 rounded-full text-slate-600 border border-slate-200">
                {colCards.length}
              </span>
            </div>
            <div className="space-y-2.5">
              {colCards.map((card) => (
                <div key={card.id} className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs space-y-2">
                  <div className="font-semibold text-xs text-slate-900 leading-snug">{card.jobTitle}</div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span>{card.clientName}</span>
                    <span className="font-bold text-emerald-700">${card.bidAmount}</span>
                  </div>
                  <Link
                    href={`/studio/${card.id}`}
                    className="block text-center text-[10px] font-bold text-emerald-600 hover:text-emerald-700 pt-1"
                  >
                    Open in Studio &rarr;
                  </Link>
                </div>
              ))}
              {colCards.length === 0 && (
                <div className="text-center py-6 text-xs text-slate-400 italic">No proposals</div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

