'use client';

import React, { useState } from 'react';

export default function MessagesPage() {
  const [replyText, setReplyText] = useState(
    'Thank you for the invitation! I would be glad to discuss the technical roadmap. I have tentatively held Nov 17, 2:00 PM UTC. Does that work for your team?'
  );
  const [messages, setMessages] = useState([
    {
      id: 'm1',
      sender: 'client',
      text: 'Hi Alex! We reviewed your proposal and were really impressed by your RAG benchmark metrics. Can we hop on a quick 20-min call this week?',
      time: '11:45 AM',
    },
  ]);

  const handleSendReply = () => {
    if (!replyText.trim()) return;
    setMessages((prev) => [
      ...prev,
      { id: `m_${Date.now()}`, sender: 'freelancer', text: replyText, time: 'Just now' },
    ]);
    setReplyText('');
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col md:flex-row min-h-[580px]">
      {/* Thread list */}
      <div className="w-full md:w-80 border-r border-slate-200 p-4 space-y-3 bg-slate-50">
        <h3 className="font-bold text-xs uppercase tracking-wider text-slate-500">Active Conversations</h3>
        <div className="bg-white p-3.5 rounded-lg border border-emerald-500/30 shadow-xs space-y-1">
          <div className="flex items-center justify-between">
            <span className="font-bold text-xs text-slate-900">HealthAI Technologies</span>
            <span className="text-[10px] text-slate-400">11:45 AM</span>
          </div>
          <p className="text-xs text-slate-600 line-clamp-1">Can we hop on a quick 20-min call this week?</p>
          <div className="pt-1">
            <span className="text-[10px] bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-0.5 rounded font-bold">
              Interview Invite
            </span>
          </div>
        </div>
      </div>

      {/* Message Chat Pane */}
      <div className="flex-1 flex flex-col justify-between p-6">
        <div className="space-y-4">
          <div className="border-b border-slate-200 pb-3 flex items-center justify-between">
            <div>
              <h2 className="font-bold text-sm text-slate-900">HealthAI Technologies</h2>
              <span className="text-xs text-slate-500">Job: Enterprise PyTorch RAG Pipeline ($3,400)</span>
            </div>
            {/* Calendar Hold Chip */}
            <div className="bg-emerald-50 border border-emerald-300 px-3 py-1.5 rounded-lg flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-semibold text-emerald-800">
                Workspace Hold: Nov 17, 2:00 PM UTC (30m)
              </span>
            </div>
          </div>

          <div className="space-y-3">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender === 'freelancer' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`p-3.5 rounded-lg text-xs max-w-lg leading-relaxed ${
                    m.sender === 'freelancer'
                      ? 'bg-emerald-600 text-white font-medium'
                      : 'bg-slate-100 text-slate-800'
                  }`}
                >
                  {m.text}
                </div>
                <span className="text-[10px] text-slate-400 mt-1">{m.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Reply Area with Human Approval Gate */}
        <div className="border-t border-slate-200 pt-4 mt-6 space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span className="font-semibold text-slate-700">Client Liaison Draft (Awaiting Your Review):</span>
            <span className="text-emerald-700 font-semibold">Platform Policy Verified Clean</span>
          </div>
          <textarea
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            rows={3}
            className="w-full text-xs p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-emerald-500"
          />
          <div className="flex justify-end">
            <button
              onClick={handleSendReply}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow-sm"
            >
              Approve & Send Message
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

