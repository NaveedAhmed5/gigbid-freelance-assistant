'use client';

import React, { useState, useEffect } from 'react';

export default function SettingsPage() {
  const [autonomy, setAutonomy] = useState('semi_autonomous');
  const [adapter, setAdapter] = useState('gigsim');
  const [profile, setProfile] = useState('open');
  const [memories, setMemories] = useState([
    {
      key: 'style_edit_01',
      type: 'Style Memory',
      content: 'User demonstrated preference for high conciseness; omit introductory fluff.',
    },
    {
      key: 'outcome_won_01',
      type: 'Outcome Memory',
      content: 'Winning pattern in Healthcare: Citing sub-50ms latency and 42% ROI directly led to HIRED offer.',
    },
  ]);
  const [statusMsg, setStatusMsg] = useState('');

  const handleDeleteMemory = (key: string) => {
    setMemories((prev) => prev.filter((m) => m.key !== key));
    setStatusMsg(`Memory '${key}' deleted.`);
    fetch(`http://localhost:8000/settings/memories/${key}`, { method: 'DELETE' }).catch(() => {});
  };

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await fetch('http://localhost:8000/settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          autonomy_level: autonomy,
          active_profile: profile,
          marketplace_adapter: adapter,
          max_critic_loops: 2,
        }),
      });
      setStatusMsg('Configuration saved successfully.');
    } catch {
      setStatusMsg('Settings updated locally.');
    }
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">System Configuration & Memory Viewer</h1>
        <p className="text-xs text-slate-500">Configure agent autonomy levels, active model profiles, and inspect persistent memories.</p>
      </div>

      {statusMsg && (
        <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs px-4 py-2.5 rounded-lg font-semibold">
          {statusMsg}
        </div>
      )}

      {/* Settings Form */}
      <form onSubmit={handleSaveSettings} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Agent Autonomy & Adapters</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Autonomy Level</label>
            <select
              value={autonomy}
              onChange={(e) => setAutonomy(e.target.value)}
              className="w-full text-xs border border-slate-300 rounded p-2 focus:ring-2 focus:ring-emerald-500 font-medium"
            >
              <option value="manual_approval">Manual (Approve every step)</option>
              <option value="semi_autonomous">Semi-Autonomous (Human gate before submit)</option>
              <option value="full_autonomous">Full-Autonomous (Demo only)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Model Profile</label>
            <select
              value={profile}
              onChange={(e) => setProfile(e.target.value)}
              className="w-full text-xs border border-slate-300 rounded p-2 focus:ring-2 focus:ring-emerald-500 font-medium"
            >
              <option value="open">Open Weights Profile (Ollama / Qwen2.5)</option>
              <option value="paid">Commercial API Profile (Frontier GPT-4o)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Marketplace Adapter</label>
            <select
              value={adapter}
              onChange={(e) => setAdapter(e.target.value)}
              className="w-full text-xs border border-slate-300 rounded p-2 focus:ring-2 focus:ring-emerald-500 font-medium"
            >
              <option value="gigsim">GigSim Simulator (Deterministic Benchmark)</option>
              <option value="upwork_live">Upwork Live MCP (OAuth 2.1 Guarded)</option>
            </select>
          </div>
        </div>

        <button
          type="submit"
          className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-sm"
        >
          Save Configuration
        </button>
      </form>

      {/* Memory Viewer */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Long-Term Memory Viewer</h3>
            <p className="text-xs text-slate-500">Learned user stylistic preferences and validated winning outcome patterns.</p>
          </div>
          <span className="text-xs bg-slate-100 px-2.5 py-1 rounded font-mono font-bold text-slate-600">
            {memories.length} Memories Active
          </span>
        </div>

        <div className="space-y-3">
          {memories.map((mem) => (
            <div key={mem.key} className="flex items-center justify-between p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs">
              <div className="space-y-1">
                <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-700 uppercase">
                  {mem.type}
                </span>
                <p className="font-medium text-slate-800">{mem.content}</p>
                <span className="text-[10px] text-slate-400 font-mono block">Key: {mem.key}</span>
              </div>
              <button
                onClick={() => handleDeleteMemory(mem.key)}
                className="text-xs text-red-600 hover:text-red-800 font-bold ml-4 underline"
              >
                Delete
              </button>
            </div>
          ))}
          {memories.length === 0 && (
            <div className="text-center py-6 text-xs text-slate-400 italic">No memories stored.</div>
          )}
        </div>
      </div>
    </div>
  );
}

