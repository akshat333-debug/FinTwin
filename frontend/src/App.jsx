import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ThemeProvider } from './components/ThemeProvider';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import DataInput from './components/DataInput';
import HealthGauge, { StatCards } from './components/HealthGauge';
import { ProfitChart, SurvivalChart } from './components/Charts';
import { RiskCards, RoadmapCards } from './components/InsightCards';
import { Zap, FileText, ArrowRight, RefreshCw } from 'lucide-react';

function AppContent() {
  const [page, setPage] = useState('dashboard');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleNavigate = (id) => {
    setPage(id);
    // For upload/synthetic pages, don't clear result — only clear on explicit action
  };

  const handleAnalysisComplete = (data) => {
    setResult(data);
    setPage('dashboard');
  };

  return (
    <div className="app-layout">
      <Sidebar activePage={page} onNavigate={handleNavigate} />

      <div className="main-area">
        <TopBar activePage={page} />

        <div className="content">
          <AnimatePresence mode="wait">
            {/* ── Dashboard ── */}
            {page === 'dashboard' && (
              <motion.div key="dashboard"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {!result && !loading ? (
                  /* Empty state */
                  <div className="empty-state">
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
                    <h3>No Analysis Yet</h3>
                    <p>Upload a CSV or generate synthetic data to see your financial stress analysis.</p>
                    <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                      <button className="btn btn-primary" onClick={() => setPage('synthetic')}>
                        <Zap size={14} /> Quick Simulation
                      </button>
                      <button className="btn btn-outline" onClick={() => setPage('upload')}>
                        Upload CSV
                      </button>
                    </div>
                  </div>
                ) : loading ? (
                  <div className="loading-overlay">
                    <div className="spinner" />
                    <p>Running Monte Carlo simulation...</p>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Analyzing 7 shock scenarios × 1,000 iterations</p>
                  </div>
                ) : (
                  /* Dashboard content */
                  <div>
                    {/* Header bar */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                      <div>
                        <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Analysis Results</h2>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          Completed in {result.elapsed_seconds}s • {result.simulations[0]?.n_simulations?.toLocaleString() || '1,000'} simulations per shock
                        </p>
                      </div>
                      <button className="btn btn-outline btn-sm" onClick={() => setPage('synthetic')}>
                        <RefreshCw size={13} /> New Analysis
                      </button>
                    </div>

                    {/* Stat cards */}
                    <div style={{ marginBottom: '1.25rem' }}>
                      <StatCards metrics={result.metrics} health={result.health} />
                    </div>

                    {/* Health + Profit */}
                    <div className="grid-2-wide" style={{ marginBottom: '1.25rem' }}>
                      <HealthGauge health={result.health} />
                      <ProfitChart metrics={result.metrics} />
                    </div>

                    {/* Survival */}
                    <div style={{ marginBottom: '1.25rem' }}>
                      <SurvivalChart simulations={result.simulations} />
                    </div>

                    {/* Risks + Roadmap */}
                    <div className="grid-2" style={{ marginBottom: '2rem' }}>
                      <RiskCards risks={result.risks} />
                      <RoadmapCards roadmap={result.roadmap} />
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Upload Page ── */}
            {page === 'upload' && (
              <motion.div key="upload"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                style={{ maxWidth: 600 }}>
                <DataInput mode="upload" onAnalysisComplete={handleAnalysisComplete} setLoading={setLoading} />
              </motion.div>
            )}

            {/* ── Synthetic Page ── */}
            {page === 'synthetic' && (
              <motion.div key="synthetic"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                style={{ maxWidth: 520 }}>
                <DataInput mode="synthetic" onAnalysisComplete={handleAnalysisComplete} setLoading={setLoading} />
              </motion.div>
            )}

            {/* ── Shocks Reference ── */}
            {page === 'shocks' && (
              <motion.div key="shocks"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <div className="card">
                  <div className="card-header">
                    <span className="card-title"><Zap size={16} className="icon" /> India-Specific Shock Models</span>
                  </div>
                  <div className="card-body">
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border)' }}>
                          <th style={{ textAlign: 'left', padding: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase' }}>Shock</th>
                          <th style={{ textAlign: 'left', padding: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase' }}>Impact</th>
                          <th style={{ textAlign: 'left', padding: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase' }}>Duration</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[
                          ['Recession', '−20% revenue', '12 months', 'danger'],
                          ['GST Hike', '+5% expenses', '12 months', 'warning'],
                          ['Fuel/Logistics Spike', '+10% expenses', '12 months', 'warning'],
                          ['Pandemic Lockdown', '−35% revenue', '3 months', 'danger'],
                          ['Credit Freeze', '−40% cash, −15% revenue', '3 months', 'danger'],
                          ['Demonetization', '−50% revenue', '2 months', 'danger'],
                          ['Inflation Shock', '+15% expenses', '12 months', 'warning'],
                        ].map(([name, impact, duration, sev]) => (
                          <tr key={name} style={{ borderBottom: '1px solid var(--border-light)' }}>
                            <td style={{ padding: '0.7rem', fontWeight: 500 }}>{name}</td>
                            <td style={{ padding: '0.7rem' }}><span className={`badge badge-${sev}`}>{impact}</span></td>
                            <td style={{ padding: '0.7rem', color: 'var(--text-secondary)' }}>{duration}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </motion.div>
            )}

            {/* ── Risks Page (standalone) ── */}
            {page === 'risks' && (
              <motion.div key="risks"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {result ? (
                  <div className="grid-2">
                    <RiskCards risks={result.risks} />
                    <RoadmapCards roadmap={result.roadmap} />
                  </div>
                ) : (
                  <div className="empty-state">
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🛡️</div>
                    <h3>No Analysis Data</h3>
                    <p>Run a simulation first to see risk analysis and recommendations.</p>
                    <button className="btn btn-primary" onClick={() => setPage('synthetic')}>
                      <Zap size={14} /> Run Simulation
                    </button>
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Docs Page ── */}
            {page === 'docs' && (
              <motion.div key="docs"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                style={{ maxWidth: 600 }}>
                <div className="card">
                  <div className="card-header">
                    <span className="card-title"><FileText size={16} className="icon" /> CSV Schema</span>
                  </div>
                  <div className="card-body">
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                      Upload a CSV with the following columns. Minimum 6 rows required.
                    </p>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border)' }}>
                          <th style={{ textAlign: 'left', padding: '0.5rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.72rem', textTransform: 'uppercase' }}>Column</th>
                          <th style={{ textAlign: 'left', padding: '0.5rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.72rem', textTransform: 'uppercase' }}>Type</th>
                          <th style={{ textAlign: 'left', padding: '0.5rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.72rem', textTransform: 'uppercase' }}>Example</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[
                          ['month', 'date (YYYY-MM)', '2024-01'],
                          ['revenue', 'number (₹)', '500000'],
                          ['fixed_costs', 'number (₹)', '120000'],
                          ['variable_costs', 'number (₹)', '180000'],
                          ['loan_emi', 'number (₹)', '25000'],
                          ['cash_reserve', 'number (₹)', '250000'],
                        ].map(([col, type, example]) => (
                          <tr key={col} style={{ borderBottom: '1px solid var(--border-light)' }}>
                            <td style={{ padding: '0.6rem', fontFamily: 'monospace', fontWeight: 600, color: 'var(--primary)' }}>{col}</td>
                            <td style={{ padding: '0.6rem', color: 'var(--text-secondary)' }}>{type}</td>
                            <td style={{ padding: '0.6rem', color: 'var(--text-muted)' }}>{example}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
