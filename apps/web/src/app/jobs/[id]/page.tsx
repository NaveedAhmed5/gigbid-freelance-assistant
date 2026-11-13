'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import RequirementEvidenceMatrix from '@/components/RequirementEvidenceMatrix';

export default function JobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = (params?.id as string) || 'job_0001';

  const [analyzing, setAnalyzing] = useState(false);

  const handleTriggerAnalysis = async () => {
    setAnalyzing(true);
    try {
      await fetch('http://localhost:8000/jobs/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ job_id: jobId }),
      });
      router.push(`/studio/${jobId}`);
    } catch {
      router.push(`/studio/${jobId}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-mono text-slate-400">Job Detail View</span>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Enterprise Architecture & RAG Ingestion Pipeline
          </h1>
        </div>
        <button
          onClick={handleTriggerAnalysis}
          data-testid="trigger-analysis-button"
          disabled={analyzing}
          className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-sm transition-colors flex items-center space-x-2"
        >
          <span>{analyzing ? 'Synthesizing Pipeline...' : 'Generate Proposal in Studio'}</span>
          <span>&rarr;</span>
        </button>
      </div>

      {/* Requirement-to-Evidence Matrix */}
      <RequirementEvidenceMatrix />

      {/* Client Profile details */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <span className="text-xs text-slate-400 block font-medium">Client Verification</span>
          <span className="text-sm font-bold text-emerald-700">Payment Verified (4.95 Rating)</span>
        </div>
        <div>
          <span className="text-xs text-slate-400 block font-medium">Historical Platform Spend</span>
          <span className="text-sm font-bold text-slate-800">$125,000+ Across 18 Contracts</span>
        </div>
        <div>
          <span className="text-xs text-slate-400 block font-medium">Hire Rate</span>
          <span className="text-sm font-bold text-slate-800">88% Hire Rate</span>
        </div>
        <div>
          <span className="text-xs text-slate-400 block font-medium">Required Connects</span>
          <span className="text-sm font-bold text-slate-800">8 Connects ($1.20)</span>
        </div>
      </div>
    </div>
  );
}

