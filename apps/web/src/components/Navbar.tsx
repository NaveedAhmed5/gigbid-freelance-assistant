'use client';

import React, { useState } from 'react';
import Link from 'next/link';

export default function Navbar() {
  const [activePersona, setActivePersona] = useState('ai_ml_engineer');

  const handlePersonaChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newPersona = e.target.value;
    setActivePersona(newPersona);
    try {
      await fetch('http://localhost:8000/auth/switch-persona', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona: newPersona }),
      });
    } catch {
      // frictionless fallback
    }
  };

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link href="/inbox" className="text-xl font-bold tracking-tight text-emerald-400 flex items-center space-x-2">
            <span>GigBid</span>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-800 px-2 py-0.5 rounded-full font-mono">
              AI-4016
            </span>
          </Link>
          <nav className="hidden md:flex space-x-5 text-sm font-medium text-slate-300">
            <Link href="/inbox" className="hover:text-emerald-400 transition-colors">Inbox</Link>
            <Link href="/pipeline" className="hover:text-emerald-400 transition-colors">Pipeline</Link>
            <Link href="/messages" className="hover:text-emerald-400 transition-colors">Messages</Link>
            <Link href="/analytics" className="hover:text-emerald-400 transition-colors">Analytics</Link>
            <Link href="/settings" className="hover:text-emerald-400 transition-colors">Settings</Link>
          </nav>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400">Active Persona:</span>
            <select
              value={activePersona}
              onChange={handlePersonaChange}
              data-testid="persona-selector"
              className="bg-slate-800 text-slate-200 text-xs rounded border border-slate-700 px-2.5 py-1 focus:outline-none focus:border-emerald-500 font-medium"
            >
              <option value="ai_ml_engineer">Dr. Alex Rivera (AI/ML)</option>
              <option value="fullstack_web_dev">Maya Lin (Full-Stack)</option>
              <option value="data_analyst">Marcus Chen (Data Analyst)</option>
            </select>
          </div>
          <Link
            href="/onboarding"
            className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded border border-slate-700"
          >
            Reviewer Demo
          </Link>
        </div>
      </div>
    </header>
  );
}
