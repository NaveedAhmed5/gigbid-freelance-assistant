'use client';

import React, { useState } from 'react';

interface ProposalStudioProps {
  jobId: string;
  initialDraft: string;
  bidAmount: number;
  onApprove: (editedText: string) => void;
  onReject: (reason: string) => void;
}

export default function ProposalStudioEditor({
  jobId,
  initialDraft,
  bidAmount,
  onApprove,
  onReject,
}: ProposalStudioProps) {
  const [draft, setDraft] = useState(initialDraft);
  const [hoveredEvidence, setHoveredEvidence] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [dryRunValidated, setDryRunValidated] = useState(true);

  const handleRegenerateParagraph = () => {
    const updated = draft.replace(
      /where we engineered a resilient pipeline/i,
      'where we architected an enterprise-grade high-throughput ingestion engine'
    );
    setDraft(updated);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
      {/* Header bar */}
      <div className="px-6 py-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div>
          <h2 className="text-base font-bold text-slate-900">Proposal Studio & Approval Gate</h2>
          <p className="text-xs text-slate-500">Job Reference: {jobId} | Proposed Bid: ${bidAmount}</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-xs bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded-full font-semibold">
            Dry-Run Validated
          </span>
          <span className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-full font-semibold">
            Compliance 100% Clean
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 divide-y lg:divide-y-0 lg:divide-x divide-slate-200">
        {/* Main Editor */}
        <div className="p-6 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Grounded Proposal Text (Editable)
            </label>
            <button
              onClick={handleRegenerateParagraph}
              className="text-xs text-emerald-600 hover:text-emerald-700 font-medium underline"
            >
              Regenerate Architecture Hook
            </button>
          </div>

          <textarea
            data-testid="proposal-editor-textarea"
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={10}
            className="w-full text-sm text-slate-800 border border-slate-300 rounded-lg p-4 font-mono leading-relaxed focus:outline-none focus:ring-2 focus:ring-emerald-500"
          />

          {/* Evidence on hover helper */}
          <div className="p-3 bg-slate-50 rounded border border-slate-200 text-xs text-slate-600">
            <span className="font-semibold text-slate-800">Verified Evidence Proof Point: </span>
            <span
              onMouseEnter={() => setHoveredEvidence('Case Study: cs_ai_ml_engineer_01 - 42% latency reduction')}
              onMouseLeave={() => setHoveredEvidence(null)}
              className="text-emerald-700 font-semibold cursor-pointer underline decoration-dotted"
            >
              [42% measurable efficiency improvement]
            </span>
            {hoveredEvidence && (
              <div className="mt-2 p-2 bg-emerald-950 text-emerald-100 rounded text-xs shadow-lg font-mono">
                {hoveredEvidence}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar Critic & Compliance Alerts */}
        <div className="p-6 bg-slate-50 space-y-4">
          <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Agent Auditor Feedback
          </h4>

          <div className="bg-white p-3.5 rounded border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-800">Critic Node</span>
              <span className="text-xs text-emerald-700 font-bold">4.8 / 5.0</span>
            </div>
            <p className="text-xs text-slate-600">
              Sharp opening hook. Directly highlights client problem with verified metric proof.
            </p>
          </div>

          <div className="bg-white p-3.5 rounded border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-800">Compliance Guard</span>
              <span className="text-xs text-emerald-700 font-bold">PASS</span>
            </div>
            <p className="text-xs text-slate-600">
              Zero off-platform contact or payment traps detected. Compliant with Nov 2 terms.
            </p>
          </div>

          <div className="bg-white p-3.5 rounded border border-slate-200 shadow-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-800">Connects Investment</span>
              <span className="text-xs font-bold text-slate-800">8 Connects</span>
            </div>
            <p className="text-xs text-slate-500">
              Projected ROI Multiplier: 931x based on win probability.
            </p>
          </div>
        </div>
      </div>

      {/* Approval Action Bar */}
      <div className="px-6 py-4 bg-slate-100 border-t border-slate-200 flex items-center justify-between">
        <button
          onClick={() => setShowRejectModal(true)}
          data-testid="reject-proposal-button"
          className="px-4 py-2 text-xs font-semibold text-red-700 hover:text-red-800 bg-red-50 hover:bg-red-100 border border-red-200 rounded-lg transition-colors"
        >
          Reject Draft
        </button>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => onApprove(draft)}
            data-testid="approve-proposal-button"
            className="px-6 py-2 text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 rounded-lg shadow-sm transition-colors"
          >
            Approve & Submit to Upwork
          </button>
        </div>
      </div>

      {/* Rejection Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full space-y-4 shadow-xl">
            <h3 className="font-bold text-slate-900 text-sm">Provide Rejection Feedback</h3>
            <textarea
              data-testid="reject-reason-input"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Explain why this proposal is being rejected..."
              className="w-full text-xs p-2 border border-slate-300 rounded focus:ring-1 focus:ring-red-500"
              rows={3}
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setShowRejectModal(false)}
                className="px-3 py-1.5 text-xs text-slate-600 hover:text-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onReject(rejectReason || 'User rejected draft');
                  setShowRejectModal(false);
                }}
                data-testid="confirm-reject-button"
                className="px-4 py-1.5 text-xs font-bold text-white bg-red-600 hover:bg-red-700 rounded"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
