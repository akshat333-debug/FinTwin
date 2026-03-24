import { useState } from 'react';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
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
import CustomShockBuilder from './components/CustomShockBuilder';
import ErrorBoundary from './components/ErrorBoundary';
import { Zap, FileText, RefreshCw, Download, Sparkles } from 'lucide-react';
import { getShocks } from './services/api';

function AppContent() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [shocksList, setShocksList] = useState([]);
  const navigate = useNavigate();
  const location = useLocation();

  // Derive active page from current route path
  const activePage = location.pathname === '/' ? 'dashboard' : location.pathname.slice(1);

  // Fetch shocks on mount
  import('react').then((React) => {
    React.useEffect(() => {
      getShocks().then(setShocksList).catch(console.error);
    }, []);
  });

  const handleAnalysisComplete = (data) => {
    setResult(data);
    navigate('/');
  };

  const handleDownloadPDF = () => {
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
      <hr/><p style="color:#94a3b8;font-size:0.75rem;">Generated by FinTwin v3.2 — MSME Financial Stress Simulator</p>
      </body></html>
    `);
    w.document.close();
    setTimeout(() => w.print(), 500);
  };

  // Page transition wrapper
  const PageTransition = ({ children }) => (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      {children}
    </motion.div>
  );

  // Empty state helper
  const EmptyState = ({ icon, title, description }) => (
    <div className="empty-state">
      <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>{icon}</div>
      <h3>{title}</h3>
      <p>{description}</p>
      <button className="btn btn-primary" onClick={() => navigate('/synthetic')}>
        <Zap size={14} /> Run Simulation
      </button>
    </div>
  );

  // ── Dashboard Page ──
  const DashboardPage = () => {
    if (!result && !loading) {
      return (
        <div className="empty-state">
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
          <h3>No Analysis Yet</h3>
          <p>Upload a CSV or generate synthetic data to see your financial stress analysis.</p>
          <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
            <button className="btn btn-primary" onClick={() => navigate('/synthetic')}>
              <Zap size={14} /> Quick Simulation
            </button>
            <button className="btn btn-outline" onClick={() => navigate('/upload')}>
              Upload CSV
            </button>
          </div>
        </div>
      );
    }
    if (loading) {
      return (
        <div className="loading-overlay">
          <div className="spinner" />
          <p>Running Monte Carlo simulation...</p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Analyzing 7 shocks × 1,000 iterations + forecast + backtesting</p>
        </div>
      );
    }
    return (
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
            <button className="btn btn-outline btn-sm" onClick={() => navigate('/synthetic')}>
              <RefreshCw size={13} /> New Analysis
            </button>
          </div>
        </div>

        {/* Stat cards */}
        <ErrorBoundary name="Stats">
          <div style={{ marginBottom: '1.25rem' }}>
            <StatCards metrics={result.metrics} health={result.health} />
          </div>
        </ErrorBoundary>

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
        <ErrorBoundary name="Health & Profit Charts">
          <div className="grid-2-wide" style={{ marginBottom: '1.25rem' }}>
            <HealthGauge health={result.health} />
            <ProfitChart metrics={result.metrics} />
          </div>
        </ErrorBoundary>

        {/* Cash Flow Forecast */}
        {result.forecast && (
          <ErrorBoundary name="Cash Flow Forecast">
            <div style={{ marginBottom: '1.25rem' }}>
              <ForecastChart forecast={result.forecast} />
            </div>
          </ErrorBoundary>
        )}

        {/* Survival */}
        <ErrorBoundary name="Survival Chart">
          <div style={{ marginBottom: '1.25rem' }}>
            <SurvivalChart simulations={result.simulations} />
          </div>
        </ErrorBoundary>

        {/* Risks + Roadmap */}
        <ErrorBoundary name="Risk Analysis">
          <div className="grid-2" style={{ marginBottom: '1.25rem' }}>
            <RiskCards risks={result.risks} />
            <RoadmapCards roadmap={result.roadmap} />
          </div>
        </ErrorBoundary>

        {/* New Analysis button */}
        <div style={{ textAlign: 'center', paddingBottom: '2rem' }}>
          <button className="btn btn-outline btn-sm" onClick={() => navigate('/synthetic')}>
            <RefreshCw size={13} /> Run Another Analysis
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-area">
        <TopBar activePage={activePage} />

        <div className="content">
          <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
              {/* Dashboard */}
              <Route path="/" element={<PageTransition><DashboardPage /></PageTransition>} />

              {/* Upload */}
              <Route path="/upload" element={
                <PageTransition>
                  <div style={{ maxWidth: 600 }}>
                    <DataInput mode="upload" onAnalysisComplete={handleAnalysisComplete} setLoading={setLoading} />
                  </div>
                </PageTransition>
              } />

              {/* Synthetic */}
              <Route path="/synthetic" element={
                <PageTransition>
                  <div style={{ maxWidth: 520 }}>
                    <DataInput mode="synthetic" onAnalysisComplete={handleAnalysisComplete} setLoading={setLoading} />
                  </div>
                </PageTransition>
              } />

              {/* Government Schemes */}
              <Route path="/schemes" element={
                <PageTransition>
                  {result?.schemes?.length ? (
                    <ErrorBoundary name="Schemes">
                      <div>
                        <div style={{ marginBottom: '1rem' }}>
                          <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Recommended Government Schemes</h2>
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            {result.schemes.length} schemes matched based on your financial profile
                          </p>
                        </div>
                        <SchemeCards schemes={result.schemes} />
                      </div>
                    </ErrorBoundary>
                  ) : <EmptyState icon="🏛️" title="No Scheme Data" description="Run a simulation first to get personalized government scheme recommendations." />}
                </PageTransition>
              } />

              {/* Cash Flow Forecast */}
              <Route path="/forecast" element={
                <PageTransition>
                  {result?.forecast ? (
                    <ErrorBoundary name="Forecast">
                      <ForecastChart forecast={result.forecast} />
                    </ErrorBoundary>
                  ) : <EmptyState icon="📈" title="No Forecast Data" description="Run a simulation first to see your 6-month cash flow forecast." />}
                </PageTransition>
              } />

              {/* Historical Backtesting */}
              <Route path="/backtest" element={
                <PageTransition>
                  {result?.backtest?.length ? (
                    <ErrorBoundary name="Backtest">
                      <div>
                        <div style={{ marginBottom: '1rem' }}>
                          <h2 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Historical Stress Backtesting</h2>
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            How your business would have fared during {result.backtest.length} real economic crises
                          </p>
                        </div>
                        <BacktestTimeline backtest={result.backtest} />
                      </div>
                    </ErrorBoundary>
                  ) : <EmptyState icon="🔄" title="No Backtest Data" description="Run a simulation to see how your business would perform during historical crises." />}
                </PageTransition>
              } />

              {/* Shocks Reference */}
              <Route path="/shocks" element={
                <PageTransition>
                  <div className="card">
                    <div className="card-header">
                      <span className="card-title"><Zap size={16} className="icon" /> India-Specific Shock Models</span>
                    </div>
                    <div className="card-body">
                      {shocksList.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '2rem' }}>
                          <span className="spinner-sm" style={{ borderColor: 'var(--text-muted)', borderTopColor: 'var(--primary)' }} />
                        </div>
                      ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                          <thead>
                            <tr style={{ borderBottom: '1px solid var(--border)' }}>
                              <th style={{ textAlign: 'left', padding: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase' }}>Shock</th>
                              <th style={{ textAlign: 'left', padding: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase' }}>Description</th>
                              <th style={{ textAlign: 'left', padding: '0.6rem', color: 'var(--text-muted)', fontWeight: 600, fontSize: '0.75rem', textTransform: 'uppercase' }}>Severity</th>
                            </tr>
                          </thead>
                          <tbody>
                            {shocksList.map((shock) => (
                              <tr key={shock.key} style={{ borderBottom: '1px solid var(--border-light)' }}>
                                <td style={{ padding: '0.7rem', fontWeight: 500 }}>{shock.name}</td>
                                <td style={{ padding: '0.7rem', color: 'var(--text-secondary)' }}>{shock.description}</td>
                                <td style={{ padding: '0.7rem' }}>
                                  <span className={`badge badge-${shock.severity === 'Very High' || shock.severity === 'High' ? 'danger' : 'warning'}`}>
                                    {shock.severity}
                                  </span>
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>
                  </div>
                </PageTransition>
              } />

              {/* Custom Shock Builder */}
              <Route path="/custom-shock" element={
                <PageTransition>
                  <div style={{ maxWidth: 640 }}>
                    <CustomShockBuilder />
                  </div>
                </PageTransition>
              } />

              {/* Risks Page */}
              <Route path="/risks" element={
                <PageTransition>
                  {result ? (
                    <ErrorBoundary name="Risk Analysis">
                      <div className="grid-2">
                        <RiskCards risks={result.risks} />
                        <RoadmapCards roadmap={result.roadmap} />
                      </div>
                    </ErrorBoundary>
                  ) : <EmptyState icon="🛡️" title="No Analysis Data" description="Run a simulation first to see risk analysis and recommendations." />}
                </PageTransition>
              } />

              {/* Docs Page */}
              <Route path="/docs" element={
                <PageTransition>
                  <div style={{ maxWidth: 600 }}>
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
                              ['payroll *', 'number (₹)', '80000'],
                              ['marketing *', 'number (₹)', '15000'],
                              ['software *', 'number (₹)', '10000'],
                              ['logistics *', 'number (₹)', '20000'],
                            ].map(([col, type, example]) => (
                              <tr key={col} style={{ borderBottom: '1px solid var(--border-light)' }}>
                                <td style={{ padding: '0.6rem', fontFamily: 'monospace', fontWeight: 600, color: col.includes('*') ? 'var(--warning)' : 'var(--primary)' }}>{col}</td>
                                <td style={{ padding: '0.6rem', color: 'var(--text-secondary)' }}>{type}</td>
                                <td style={{ padding: '0.6rem', color: 'var(--text-muted)' }}>{example}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.75rem' }}>
                          * Optional columns — when provided, the AI can give more specific cost-cutting advice.
                        </p>
                      </div>
                    </div>
                  </div>
                </PageTransition>
              } />
            </Routes>
          </AnimatePresence>
        </div>
      </div>

      {/* Chat FAB + Panel — context aware */}
      <ChatPanel result={result} activePage={activePage} />
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
