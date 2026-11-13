'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProposalStudioEditor from '@/components/ProposalStudioEditor';

export default function StudioPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = (params?.id as string) || 'job_0001';

  const [notification, setNotification] = useState<string | null>(null);

  const defaultDraft = `Hi team — your objective for Enterprise Architecture directly matches a recent production deployment where we engineered a resilient pipeline delivering a 42.0% efficiency improvement.

To achieve your core deliverable (Develop and deploy architecture for this project), I recommend deploying a decoupled architecture using Python, PyTorch, and FastAPI. This ensures strict type safety, sub-50ms latency, and automated verification.

In our High-Throughput Enterprise Ingestion Engine project (Healthcare), this exact architecture enabled zero-downtime scaling and reduced operational overhead by 42.0%.

Would you be open to a 15-minute technical discussion this week to review the architectural roadmap?`;

  const handleApprove = async (editedText: string) => {
    try {
      await fetch('http://localhost:8000/approvals/decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          action: 'approve',
          edited_cover_letter: editedText,
        }),
      });
      setNotification('Proposal approved and committed! Connects spent: 8.');
      setTimeout(() => router.push('/pipeline'), 1500);
    } catch {
      setNotification('Proposal approved in demo mode.');
      setTimeout(() => router.push('/pipeline'), 1500);
    }
  };

  const handleReject = async (reason: string) => {
    try {
      await fetch('http://localhost:8000/approvals/decision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          job_id: jobId,
          action: 'reject',
          feedback: reason,
        }),
      });
      setNotification(`Draft rejected: ${reason}`);
      setTimeout(() => router.push('/inbox'), 1500);
    } catch {
      setNotification(`Draft rejected in demo mode: ${reason}`);
      setTimeout(() => router.push('/inbox'), 1500);
    }
  };

  return (
    <div className="space-y-6">
      {notification && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 px-4 py-3 rounded-lg text-sm font-semibold">
          {notification}
        </div>
      )}

      <ProposalStudioEditor
        jobId={jobId}
        initialDraft={defaultDraft}
        bidAmount={3400}
        onApprove={handleApprove}
        onReject={handleReject}
      />
    </div>
  );
}
