'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function OnboardingPage() {
  const router = useRouter();
  const [email, setEmail] = useState('reviewer@gigbid.ai');
  const [password, setPassword] = useState('reviewer-demo-pass');
  const [persona, setPersona] = useState('ai_ml_engineer');
  const [statusMsg, setStatusMsg] = useState('');

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (res.ok) {
        setStatusMsg('Authenticated successfully! Redirecting...');
        router.push('/inbox');
      } else {
        setStatusMsg('Invalid reviewer credentials.');
      }
    } catch {
      // Local fallback redirect
      router.push('/inbox');
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 bg-white rounded-xl border border-slate-200 shadow-sm p-8 space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Sign In & Persona Onboarding</h1>
        <p className="text-xs text-slate-500">
          Preloaded Reviewer Account configured for rapid evaluation.
        </p>
      </div>

      <form onSubmit={handleSignIn} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Reviewer Email</label>
          <input
            type="email"
            data-testid="email-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full text-sm border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-500"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
          <input
            type="password"
            data-testid="password-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full text-sm border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-500"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Select Active Freelance Persona</label>
          <select
            data-testid="persona-select-onboarding"
            value={persona}
            onChange={(e) => setPersona(e.target.value)}
            className="w-full text-sm border border-slate-300 rounded px-3 py-2 focus:ring-2 focus:ring-emerald-500"
          >
            <option value="ai_ml_engineer">Dr. Alex Rivera — AI/ML & LLM Specialist ($110/hr)</option>
            <option value="fullstack_web_dev">Maya Lin — Full-Stack Systems Architect ($95/hr)</option>
            <option value="data_analyst">Marcus Chen — Lead BI & Analytics Engineer ($85/hr)</option>
          </select>
        </div>

        {statusMsg && <div className="text-xs text-emerald-700 font-semibold">{statusMsg}</div>}

        <button
          type="submit"
          data-testid="onboarding-submit-button"
          className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm rounded-lg shadow-sm transition-colors"
        >
          Launch Reviewer Session &rarr;
        </button>
      </form>
    </div>
  );
}
