import React, { useState } from 'react';
import {
  Cpu,
  FileCheck,
  CheckCircle2,
} from 'lucide-react';

interface AgentNode {
  id: string;
  name: string;
  role: string;
  sentiment: 'bullish' | 'neutral' | 'cautious';
  color: string;
  thesis: string;
  evidence: string;
  x: number;
  y: number;
}

const AGENTS: AgentNode[] = [
  {
    id: 'fundamental',
    name: 'Fundamental Agent',
    role: 'Moat & Pricing Defensibility',
    sentiment: 'bullish',
    color: '#06b6d4',
    thesis: 'Data Center revenue +154% YoY ($26.3B). Software moat (CUDA) defensible.',
    evidence: 'SEC 10-Q Item 2 (Data Center Segment)',
    x: 100,
    y: 70,
  },
  {
    id: 'valuation',
    name: 'Valuation Specialist',
    role: 'Multiples & FCF Projections',
    sentiment: 'neutral',
    color: '#818cf8',
    thesis: '51.8x EV/EBITDA requires >70% gross margins through FY26.',
    evidence: 'Financial Statement Multiple Decomposition',
    x: 100,
    y: 190,
  },
  {
    id: 'macro',
    name: 'Macro Risk Officer',
    role: 'Supply & Customer Exposure',
    sentiment: 'cautious',
    color: '#f59e0b',
    thesis: 'Top 4 hyperscalers generate ~40% of revenue. Capex concentration risk.',
    evidence: 'Customer Segment Footnote 8 Disclosures',
    x: 100,
    y: 310,
  },
];

export const MultiAgentNetworkVisual: React.FC = () => {
  const [selectedAgentId, setSelectedAgentId] = useState<string>('fundamental');
  const [viewState, setViewState] = useState<'consensus' | 'debate'>('consensus');

  const selectedAgent = AGENTS.find((a) => a.id === selectedAgentId) || AGENTS[0];

  return (
    <div className="w-full max-w-5xl mx-auto rounded-3xl bg-surface-200/90 border border-border-strong p-6 sm:p-8 backdrop-blur-xl font-sans text-left relative overflow-hidden shadow-2xl">
      {/* Background Grid Pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none" />

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-5 mb-6 border-b border-border-subtle relative z-10">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/10 border border-brand-500/30 text-brand-300 text-xs font-semibold uppercase tracking-wider mb-2">
            <Cpu className="w-3.5 h-3.5 text-brand-cyan" />
            <span>Autonomous Multi-Agent Deliberation</span>
          </div>
          <h3 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
            Specialized Agents Debate Evidence Before Synthesizing Consensus
          </h3>
        </div>

        {/* State Toggle */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-surface-100/90 border border-border-subtle text-xs font-mono">
          <button
            onClick={() => setViewState('consensus')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              viewState === 'consensus'
                ? 'bg-brand-emerald text-white font-bold shadow-glow-emerald'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Consensus View (88%)
          </button>
          <button
            onClick={() => setViewState('debate')}
            className={`px-3 py-1.5 rounded-lg transition-all ${
              viewState === 'debate'
                ? 'bg-brand-500 text-white font-bold shadow-glow-brand'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Active Debate Nodes
          </button>
        </div>
      </div>

      {/* Main Interactive Node Graph Viewport */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center relative z-10">
        {/* Left Column: Interactive Network Diagram (SVG) */}
        <div className="lg:col-span-7 p-3 rounded-2xl bg-surface-400/90 border border-border-subtle">
          <svg viewBox="0 0 460 380" className="w-full h-80 select-none">
            <defs>
              <linearGradient id="flowGrad1" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#06b6d4" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
              <linearGradient id="flowGrad2" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
              <linearGradient id="flowGrad3" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
            </defs>

            {/* Connecting Conduits with animated stroke dashes */}
            <path
              d="M 170 70 C 260 70, 260 190, 340 190"
              fill="none"
              stroke="url(#flowGrad1)"
              strokeWidth="2.5"
              strokeDasharray="6 4"
              className="animate-dash-flow"
            />
            <path
              d="M 170 190 L 340 190"
              fill="none"
              stroke="url(#flowGrad2)"
              strokeWidth="2.5"
              strokeDasharray="6 4"
              className="animate-dash-flow"
            />
            <path
              d="M 170 310 C 260 310, 260 190, 340 190"
              fill="none"
              stroke="url(#flowGrad3)"
              strokeWidth="2.5"
              strokeDasharray="6 4"
              className="animate-dash-flow"
            />

            {/* 3 Left Agent Nodes */}
            {AGENTS.map((agent) => {
              const isSelected = selectedAgentId === agent.id;
              return (
                <g
                  key={agent.id}
                  className="cursor-pointer"
                  onClick={() => setSelectedAgentId(agent.id)}
                >
                  {/* Node Box */}
                  <rect
                    x="20"
                    y={agent.y - 30}
                    width="150"
                    height="60"
                    rx="12"
                    fill={isSelected ? '#1e2430' : '#12161f'}
                    stroke={isSelected ? agent.color : 'rgba(255,255,255,0.12)'}
                    strokeWidth={isSelected ? '2' : '1'}
                  />
                  {/* Status indicator dot */}
                  <circle cx="36" cy={agent.y - 12} r="4" fill={agent.color} />
                  <text
                    x="48"
                    y={agent.y - 8}
                    fill="#ffffff"
                    fontSize="11"
                    fontWeight="bold"
                    fontFamily="sans-serif"
                  >
                    {agent.name}
                  </text>
                  <text
                    x="36"
                    y={agent.y + 12}
                    fill="#94a3b8"
                    fontSize="9"
                    fontFamily="sans-serif"
                  >
                    {agent.role.slice(0, 24)}...
                  </text>
                </g>
              );
            })}

            {/* Right Consensus Hub Node */}
            <g>
              <rect
                x="330"
                y="140"
                width="110"
                height="100"
                rx="16"
                fill="#161a24"
                stroke="#10b981"
                strokeWidth="2"
                className="shadow-glow-emerald"
              />
              <circle cx="385" cy="175" r="16" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" strokeWidth="1.5" />
              <text x="385" y="180" textAnchor="middle" fill="#10b981" fontSize="14" fontWeight="bold">
                ✓
              </text>
              <text
                x="385"
                y="210"
                textAnchor="middle"
                fill="#ffffff"
                fontSize="11"
                fontWeight="bold"
                fontFamily="sans-serif"
              >
                Synthesized
              </text>
              <text
                x="385"
                y="226"
                textAnchor="middle"
                fill="#10b981"
                fontSize="9"
                fontWeight="bold"
                fontFamily="monospace"
              >
                88% Conviction
              </text>
            </g>
          </svg>
        </div>

        {/* Right Column: Selected Node Inspector */}
        <div className="lg:col-span-5 space-y-4">
          <div className="p-4 rounded-2xl bg-surface-100/90 border border-brand-500/30 text-xs">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-border-subtle">
              <span className="font-bold text-white text-sm">{selectedAgent.name}</span>
              <span
                className="text-[10px] font-mono uppercase px-2 py-0.5 rounded border"
                style={{
                  color: selectedAgent.color,
                  borderColor: `${selectedAgent.color}40`,
                  backgroundColor: `${selectedAgent.color}15`,
                }}
              >
                {selectedAgent.sentiment}
              </span>
            </div>

            <div className="text-slate-300 mb-3 leading-relaxed">
              <strong>Thesis:</strong> "{selectedAgent.thesis}"
            </div>

            <div className="p-2.5 rounded-xl bg-surface-200/70 border border-border-subtle flex items-start gap-2 text-[11px] font-mono text-slate-300">
              <FileCheck className="w-4 h-4 text-brand-cyan shrink-0 mt-0.5" />
              <span><strong>Grounding:</strong> {selectedAgent.evidence}</span>
            </div>
          </div>

          <div className="p-4 rounded-2xl bg-brand-emerald/10 border border-brand-emerald/30 text-xs text-brand-emerald">
            <div className="flex items-center gap-1.5 font-bold mb-1">
              <CheckCircle2 className="w-4 h-4" />
              <span>Multi-Agent Safeguard Active</span>
            </div>
            <p className="text-slate-300 text-xs leading-relaxed">
              Consensus requires cross-validation across all 3 agent disciplines before generating recommendations.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
