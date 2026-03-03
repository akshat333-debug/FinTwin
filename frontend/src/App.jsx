import { useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ThemeProvider } from './components/ThemeProvider';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import DataInput from './components/DataInput';
import HealthGauge, { StatCards } from './components/HealthGauge';
import { ProfitChart, SurvivalChart } from './components/Charts';
import { RiskCards, RoadmapCards } from './components/InsightCards';
import SchemeCards from './components/SchemeCards';
import ForecastChart from './components/ForecastChart';
import BacktestTimeline from './components/BacktestTimeline';
import ChatPanel from './components/ChatPanel';
import { Zap, FileText, RefreshCw, Download, Sparkles } from 'lucide-react';

function AppContent() {
  const [page, setPage] = useState('dashboard');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleNavigate = (id) => setPage(id);

  const handleAnalysisComplete = (data) => {
    setResult(data);
    setPage('dashboard');
  };

  const handleDownloadPDF = () => {
    // Print-friendly PDF download
    const printContent = document.getElementById('dashboard-content');
    if (!printContent) return;
    const w = window.open('', '_blank');
    w.document.write(`
      <html><head><title>FinTwin Report</title>
      <style>
        body { font-family: Inter, sans-serif; background: #fff; color: #0f172a; padding: 2rem; }
        .stat-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
        .card { border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        h2 { font-size: 1.2rem; margin-bottom: 0.5rem; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: 600; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.5rem; border-bottom: 1px solid #e2e8f0; text-align: left; font-size: 0.82rem; }
        @media print { body { -webkit-print-color-adjust: exact; } }
      </style>
      </head><body>
      <h1>🔬 FinTwin — MSME Stress Analysis Report</h1>
      <p>Generated: ${new Date().toLocaleDateString('en-IN', { dateStyle: 'long' })}</p>
      <hr/>
      <h2>📊 Key Metrics</h2>
      <table>
        <tr><th>Metric</th><th>Value</th></tr>
        <tr><td>Avg Revenue</td><td>₹${(result?.metrics?.avg_revenue || 0).toLocaleString('en-IN')}</td></tr>
        <tr><td>Avg Monthly Profit</td><td>₹${(result?.metrics?.avg_monthly_profit || 0).toLocaleString('en-IN')}</td></tr>
        <tr><td>Cash Reserve</td><td>₹${(result?.metrics?.latest_cash_reserve || 0).toLocaleString('en-IN')}</td></tr>
        <tr><td>Profit Margin</td><td>${((result?.metrics?.avg_profit_margin || 0) * 100).toFixed(1)}%</td></tr>
        <tr><td>Revenue Volatility</td><td>${((result?.metrics?.revenue_volatility || 0) * 100).toFixed(1)}%</td></tr>
      </table>
      <h2>🏥 Health Score</h2>
      <p><strong>${result?.health?.health_score}/10 — ${result?.health?.grade}</strong></p>
      <p>${result?.health?.interpretation}</p>
      <h2>⚡ Stress Test Results</h2>
      <table>
        <tr><th>Shock Scenario</th><th>Survival %</th><th>Avg Months</th></tr>
        ${(result?.simulations || []).map(s => `<tr><td>${s.shock_name}</td><td>${s.survival_percentage.toFixed(1)}%</td><td>${s.avg_months_survived.toFixed(1)}</td></tr>`).join('')}
      </table>
      <h2>📈 Cash Flow Forecast</h2>
      <table>
        <tr><th>Month</th><th>Pessimistic (P10)</th><th>Expected (P50)</th><th>Optimistic (P90)</th></tr>
        ${(result?.forecast?.months || []).map((m, i) => `<tr><td>${m}</td><td>₹${(result.forecast.p10[i] || 0).toLocaleString('en-IN')}</td><td>₹${(result.forecast.p50[i] || 0).toLocaleString('en-IN')}</td><td>₹${(result.forecast.p90[i] || 0).toLocaleString('en-IN')}</td></tr>`).join('')}
      </table>
      <p>Bankruptcy probability (6 months): <strong>${((result?.forecast?.prob_bankrupt_by_end || 0) * 100).toFixed(1)}%</strong></p>
      <h2>🛡️ Top Risks</h2>
      ${(result?.risks || []).map(r => `<div style="margin-bottom: 0.5rem;"><strong>[${r.severity}] ${r.risk_name}</strong><br/>${r.explanation}<br/><em>${r.evidence}</em></div>`).join('')}
      <h2>🗺️ Action Roadmap</h2>
      ${(result?.roadmap || []).map(a => `<div style="margin-bottom: 0.5rem;"><strong>#${a.priority} [${a.category}] ${a.action}</strong><br/>Impact: ${a.impact} • Timeline: ${a.timeline}</div>`).join('')}
      <h2>🏛️ Recommended Government Schemes</h2>
      ${(result?.schemes || []).map(s => `<div style="margin-bottom: 0.5rem;"><strong>${s.icon} ${s.name}</strong> (Relevance: ${s.relevance_score}%)<br/>${s.reason}<br/>Max: ${s.max_amount} • ${s.eligibility}</div>`).join('')}
      <h2>🔄 Historical Backtesting</h2>
      <table>
        <tr><th>Event</th><th>Period</th><th>Survived</th><th>Cash Change</th></tr>
        ${(result?.backtest || []).map(b => `<tr><td>${b.icon} ${b.event_name}</td><td>${b.period}</td><td>${b.survived ? '✓ Yes' : '✗ No (M' + b.bankruptcy_month + ')'}</td><td>${b.cash_change_pct > 0 ? '+' : ''}${b.cash_change_pct}%</td></tr>`).join('')}
      </table>
      <hr/><p style="color:#94a3b8;font-size:0.75rem;">Generated by FinTwin v3.0 — MSME Financial Stress Simulator</p>
      </body></html>
    `);
    w.document.close();
    setTimeout(() => w.print(), 500);
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
              <motion.div key="dashboard" id="dashboard-content"
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {!result && !loading ? (
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
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Analyzing 7 shocks × 1,000 iterations + forecast + backtesting</p>
                  </div>
                ) : (
                  <div>
                    {/* Header */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                      <div>
                        <h2 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Analysis Results</h2>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          Completed in {result.elapsed_seconds}s • {result.simulations[0]?.n_simulations?.toLocaleString()} sims/shock
                        </p>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button className="btn btn-primary btn-sm" onClick={handleDownloadPDF}>
                          <Download size={13} /> Download Report
                        </button>
                        <button className="btn btn-outline btn-sm" onClick={() => setPage('synthetic')}>
                          <RefreshCw size={13} /> New Analysis
                        </button>
                      </div>
                    </div>

                    {/* Stat cards */}
                    <div style={{ marginBottom: '1.25rem' }}>
                      <StatCards metrics={result.metrics} health={result.health} />
                    </div>

                    {/* AI Executive Summary */}
                    {result.ai_summary && (
                      <div className="ai-summary" style={{ marginBottom: '1.25rem' }}>
                        <div className="ai-summary-label">
                          <Sparkles size={12} />
                          AI Executive Summary
                          {result.llm_provider && result.llm_provider !== 'mock' && (
                            <span className="badge badge-primary" style={{ marginLeft: '0.5rem', fontSize: '0.6rem' }}>
                              {result.llm_provider === 'openai' ? 'GPT-4o' : 'Gemini 2.0'}
                            </span>
                          )}
                        </div>
                        <div>{result.ai_summary}</div>
                      </div>
                    )}

                    {/* Health + Profit */}
                    <div className="grid-2-wide" style={{ marginBottom: '1.25rem' }}>
                      <HealthGauge health={result.health} />
                      <ProfitChart metrics={result.metrics} />
                    </div>

                    {/* Cash Flow Forecast */}
                    {result.forecast && (
                      <div style={{ marginBottom: '1.25rem' }}>
                        <ForecastChart forecast={result.forecast} />
                      </div>
                    )}

                    {/* Survival */}
                    <div style={{ marginBottom: '1.25rem' }}>
                      <SurvivalChart simulations={result.simulations} />
                    </div>

                    {/* Risks + Roadmap */}
                    <div className="grid-2" style={{ marginBottom: '1.25rem' }}>
                      <RiskCards risks={result.risks} />
                      <RoadmapCards roadmap={result.roadmap} />
                    </div>

                    {/* New Analysis button */}
                    <div style={{ textAlign: 'center', paddingBottom: '2rem' }}>
                      <button className="btn btn-outline btn-sm" onClick={() => setPage('synthetic')}>
                        <RefreshCw size={13} /> Run Another Analysis
                      </button>
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Upload Page ── */}
            {page === 'upload' && (
              <motion.div key="upload" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ maxWidth: 600 }}>
                <DataInput mode="upload" onAnalysisComplete={handleAnalysisComplete} setLoading={setLoading} />
              </motion.div>
            )}

            {/* ── Synthetic Page ── */}
            {page === 'synthetic' && (
              <motion.div key="synthetic" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ maxWidth: 520 }}>
                <DataInput mode="synthetic" onAnalysisComplete={handleAnalysisComplete} setLoading={setLoading} />
              </motion.div>
            )}

            {/* ── Government Schemes ── */}
            {page === 'schemes' && (
              <motion.div key="schemes" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {result?.schemes?.length ? (
                  <div>
                    <div style={{ marginBottom: '1rem' }}>
                      <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Recommended Government Schemes</h2>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {result.schemes.length} schemes matched based on your financial profile
                      </p>
                    </div>
                    <SchemeCards schemes={result.schemes} />
                  </div>
                ) : (
                  <div className="empty-state">
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏛️</div>
                    <h3>No Scheme Data</h3>
                    <p>Run a simulation first to get personalized government scheme recommendations.</p>
                    <button className="btn btn-primary" onClick={() => setPage('synthetic')}>
                      <Zap size={14} /> Run Simulation
                    </button>
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Cash Flow Forecast ── */}
            {page === 'forecast' && (
              <motion.div key="forecast" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {result?.forecast ? (
                  <ForecastChart forecast={result.forecast} />
                ) : (
                  <div className="empty-state">
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📈</div>
                    <h3>No Forecast Data</h3>
                    <p>Run a simulation first to see your 6-month cash flow forecast.</p>
                    <button className="btn btn-primary" onClick={() => setPage('synthetic')}>
                      <Zap size={14} /> Run Simulation
                    </button>
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Historical Backtesting ── */}
            {page === 'backtest' && (
              <motion.div key="backtest" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                {result?.backtest?.length ? (
                  <div>
                    <div style={{ marginBottom: '1rem' }}>
                      <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Historical Stress Backtesting</h2>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        How your business would have fared during {result.backtest.length} real economic crises
                      </p>
                    </div>
                    <BacktestTimeline backtest={result.backtest} />
                  </div>
                ) : (
                  <div className="empty-state">
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔄</div>
                    <h3>No Backtest Data</h3>
                    <p>Run a simulation to see how your business would perform during historical crises.</p>
                    <button className="btn btn-primary" onClick={() => setPage('synthetic')}>
                      <Zap size={14} /> Run Simulation
                    </button>
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Shocks Reference ── */}
            {page === 'shocks' && (
              <motion.div key="shocks" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
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

            {/* ── Risks Page ── */}
            {page === 'risks' && (
              <motion.div key="risks" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
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
              <motion.div key="docs" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ maxWidth: 600 }}>
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

      {/* Chat FAB + Panel */}
      <ChatPanel result={result} />
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
