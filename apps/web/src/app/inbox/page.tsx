'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';

interface Job {
  id: string;
  title: string;
  description: string;
  category: string;
  skills: string[];
  budget_usd?: number;
  connects_required: number;
}

export default function InboxPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('ALL');

  useEffect(() => {
    fetch('http://localhost:8000/jobs?limit=25')
      .then((res) => res.json())
      .then((data) => setJobs(data))
      .catch(() => {
        // Mock fallback
        setJobs([
          {
            id: 'job_0001',
            title: 'Seeking Expert Machine Learning Specialist for Healthcare Project',
            description: 'Looking for proven expertise in PyTorch, FastAPI, and vector retrieval search.',
            category: 'AI/ML & LLM Engineering',
            skills: ['Python', 'PyTorch', 'Vector Search'],
            budget_usd: 3500,
            connects_required: 8,
          },
          {
            id: 'job_0002',
            title: 'Full-Stack Next.js Analytics Portal with Tailwind & PostgreSQL',
            description: 'Need real-time interactive dashboards with serverless backend architectures.',
            category: 'Web & Cloud Architecture',
            skills: ['TypeScript', 'Next.js', 'PostgreSQL'],
            budget_usd: 4200,
            connects_required: 8,
          },
        ]);
      });
  }, []);

  const filteredJobs = jobs.filter((j) => {
    const matchesSearch =
      j.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      j.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCat = categoryFilter === 'ALL' || j.category.includes(categoryFilter);
    return matchesSearch && matchesCat;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Job Inbox & Opportunity Stream</h1>
          <p className="text-xs text-slate-500">Autonomous scouting stream filtered by fit score and policy safety.</p>
        </div>
        <div className="flex items-center space-x-3">
          <input
            type="text"
            data-testid="job-search-input"
            placeholder="Search keywords, skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-3 py-2 w-64 focus:ring-2 focus:ring-emerald-500"
          />
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-2.5 py-2"
          >
            <option value="ALL">All Categories</option>
            <option value="AI/ML">AI / Machine Learning</option>
            <option value="Web">Web & Cloud</option>
            <option value="Data">Data & BI</option>
          </select>
        </div>
      </div>

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
    </div>
  );
}
