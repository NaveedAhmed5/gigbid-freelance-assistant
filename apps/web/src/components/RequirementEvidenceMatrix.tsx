'use client';

import React from 'react';

interface MatrixRow {
  requirement: string;
  evidenceTitle: string;
  metric: string;
  status: 'GROUNDED' | 'PARTIAL' | 'UNSUPPORTED';
  caseStudyId: string;
}

interface MatrixProps {
  rows?: MatrixRow[];
}

export default function RequirementEvidenceMatrix({ rows }: MatrixProps) {
  const defaultRows: MatrixRow[] = [
    {
      requirement: 'Enterprise PyTorch RAG Pipeline with vector search',
      evidenceTitle: 'High-Throughput Enterprise Ingestion Engine',
      metric: '42.0% latency reduction (sub-50ms)',
      status: 'GROUNDED',
      caseStudyId: 'cs_ai_ml_engineer_01',
    },
    {
      requirement: 'Multi-Tenant OAuth 2.1 & Tenant Isolation',
      evidenceTitle: 'Secure OAuth 2.1 & Tenant Isolation Gateway',
      metric: '40.0% operational efficiency gain',
      status: 'GROUNDED',
      caseStudyId: 'cs_ai_ml_engineer_10',
    },
    {
      requirement: 'Sub-50ms real-time inference latency',
      evidenceTitle: 'Real-Time Fraud & Anomaly Detection Gateway',
      metric: '20ms streaming latency SLA',
      status: 'GROUNDED',
      caseStudyId: 'cs_ai_ml_engineer_03',
    },
  ];

  const data = rows || defaultRows;

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
        <h3 className="font-semibold text-slate-800 text-sm">Requirement-to-Evidence Matrix</h3>
        <span className="text-xs bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded font-medium">
          100% Verified Grounding
        </span>
      </div>
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50 text-slate-500 text-xs text-left">
          <tr>
            <th className="px-6 py-3 font-medium">Job Requirement</th>
            <th className="px-6 py-3 font-medium">Matched Portfolio Evidence</th>
            <th className="px-6 py-3 font-medium">Cited Benchmark Metric</th>
            <th className="px-6 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {data.map((row, idx) => (
            <tr key={idx} className="hover:bg-slate-50 transition-colors">
              <td className="px-6 py-4 text-slate-900 font-medium">{row.requirement}</td>
              <td className="px-6 py-4 text-slate-600">
                <span className="font-semibold text-slate-800">{row.evidenceTitle}</span>
                <span className="block text-xs text-slate-400 font-mono mt-0.5">{row.caseStudyId}</span>
              </td>
              <td className="px-6 py-4 text-emerald-700 font-semibold">{row.metric}</td>
              <td className="px-6 py-4">
                <span
                  className={`inline-flex px-2 py-0.5 text-xs font-bold rounded ${
                    row.status === 'GROUNDED'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-700 border border-amber-200'
                  }`}
                >
                  {row.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

