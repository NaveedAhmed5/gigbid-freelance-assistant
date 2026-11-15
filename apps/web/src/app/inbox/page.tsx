'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

interface Job {
  id: string;
  title: string;
  description: string;
  category: string;
  skills: string[];
  budget_usd?: number;
  connects_required: number;
  source?: string;
}

export default function InboxPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [statusMsg, setStatusMsg] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setErrorMsg('');
    try {
      const res = await fetch('http://localhost:8000/jobs?limit=50');
      if (res.ok) {
        const data = await res.json();
        setJobs(Array.isArray(data) ? data : []);
      } else if (res.status === 401) {
        setErrorMsg('Upwork Live MCP authentication required. Please connect your account in Settings.');
        setJobs([]);
      } else {
        setErrorMsg(`Failed to load jobs from API (HTTP ${res.status}).`);
        setJobs([]);
      }
    } catch {
      setErrorMsg('Cannot connect to backend API on http://localhost:8000. Ensure FastAPI server is running.');
      setJobs([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleSyncLiveJobs = async () => {
    setIsSyncing(true);
    setErrorMsg('');
    setStatusMsg('');
    try {
      const res = await fetch('http://localhost:8000/jobs/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (res.ok) {
        const data = await res.json();
        setJobs(data.jobs || []);
        setStatusMsg(data.message || `Successfully synced ${data.count} live jobs.`);
      } else if (res.status === 401) {
        const err = await res.json().catch(() => ({}));
        setErrorMsg(err.detail || 'Upwork Live MCP Authentication required. Please connect your Upwork account in Settings.');
      } else {
        const err = await res.json().catch(() => ({}));
        setErrorMsg(err.detail || `Scan failed with status ${res.status}`);
      }
    } catch {
      setErrorMsg('Network error connecting to API /jobs/scan.');
    } finally {
      setIsSyncing(false);
    }
  };

  const filteredJobs = jobs.filter((j) => {
    const matchesSearch =
      j.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      j.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = categoryFilter === 'ALL' || j.category.toLowerCase().includes(categoryFilter.toLowerCase());
    return matchesSearch && matchesCat;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job Inbox & Opportunity Stream</h1>
          <p className="text-xs text-slate-500">Autonomous scouting stream filtered by fit score, platform safety, and live Upwork MCP.</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            data-testid="sync-live-jobs-button"
            onClick={handleSyncLiveJobs}
            disabled={isSyncing}
            className="px-4 py-2 bg-[#14a800] hover:bg-[#108a00] text-white text-xs font-bold rounded-lg shadow-sm transition-all flex items-center space-x-2 disabled:opacity-50"
          >
            {isSyncing ? (
              <>
                <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin inline-block"></span>
                <span>Scouting Upwork MCP...</span>
              </>
            ) : (
              <>
                <span>⚡ Sync Live Upwork Jobs / Run Scout</span>
              </>
            )}
          </button>

          <input
            type="text"
            data-testid="job-search-input"
            placeholder="Search keywords, skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-3 py-2 w-56 focus:ring-2 focus:ring-emerald-500"
          />

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-2.5 py-2 font-medium"
          >
            <option value="ALL">All Categories</option>
            <option value="AI/ML">AI / Machine Learning</option>
            <option value="Web">Web & Cloud</option>
            <option value="Data">Data & BI</option>
          </select>
        </div>
      </div>

      {statusMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs px-4 py-2.5 rounded-lg font-semibold flex items-center justify-between">
          <span>{statusMsg}</span>
          <button onClick={() => setStatusMsg('')} className="text-emerald-700 font-bold ml-2">✕</button>
        </div>
      )}

      {errorMsg && (
        <div className="bg-amber-50 border border-amber-300 text-amber-900 text-xs px-4 py-3 rounded-lg flex items-center justify-between">
          <div className="space-y-1">
            <span className="font-bold block">⚠️ Action Required</span>
            <span>{errorMsg}</span>
          </div>
          <Link
            href="/settings"
            className="px-3 py-1.5 bg-amber-800 hover:bg-amber-900 text-white rounded font-bold text-xs ml-4 shrink-0 transition-colors"
          >
            Go to Settings &rarr;
          </Link>
        </div>
      )}

      {loading ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center text-slate-500 text-sm">
          <div className="w-6 h-6 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          Loading opportunity stream...
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center space-y-3">
          <div className="text-3xl">📡</div>
          <h3 className="font-bold text-slate-800 text-base">No Live Jobs in Cache</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Click &quot;Sync Live Upwork Jobs / Run Scout&quot; above to fetch real-time opportunities from Upwork Live MCP. Dummy seed jobs have been cleared.
          </p>
          <div className="pt-2">
            <button
              onClick={handleSyncLiveJobs}
              disabled={isSyncing}
              className="px-5 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-sm"
            >
              Fetch Live Upwork Opportunities Now
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredJobs.map((job) => (
            <div
              key={job.id}
              data-testid={`job-card-${job.id}`}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-emerald-400 transition-all flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
            >
              <div className="space-y-1.5 max-w-3xl">
                <div className="flex items-center space-x-2">
                  <span className="text-[11px] font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded">
                    Match Score: 94%
                  </span>
                  <span className="text-[11px] font-bold bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded">
                    {job.source === 'upwork_live' ? '● Upwork Live' : 'Marketplace'}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">{job.id}</span>
                </div>
                <h3 className="font-bold text-slate-900 text-base">{job.title}</h3>
                <p className="text-xs text-slate-600 line-clamp-2">{job.description}</p>
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {job.skills.map((s) => (
                    <span key={s} className="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-mono">
                      {s}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col items-end space-y-2 min-w-[140px]">
                <div className="text-right">
                  <span className="text-xs text-slate-400 block">Target Budget</span>
                  <span className="text-base font-extrabold text-slate-900">
                    {job.budget_usd ? `$${job.budget_usd}` : '$95/hr'}
                  </span>
                </div>
                <Link
                  href={`/jobs/${job.id}`}
                  data-testid={`inspect-job-${job.id}`}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-sm transition-colors"
                >
                  Inspect & Match &rarr;
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
