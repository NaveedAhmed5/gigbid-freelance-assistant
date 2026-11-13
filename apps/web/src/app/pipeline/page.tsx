'use client';

import React from 'react';
import KanbanBoard from '@/components/KanbanBoard';

export default function PipelinePage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Proposal Pipeline & Kanban Board</h1>
          <p className="text-xs text-slate-500">Track lifecycle from initial draft generation to client contract win.</p>
        </div>
      </div>

      <KanbanBoard />
    </div>
  );
}

