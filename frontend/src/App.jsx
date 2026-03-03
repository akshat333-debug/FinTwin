import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, BarChart3, AlertTriangle, Map, Zap, ArrowLeft, Clock } from 'lucide-react';
import DataInput from './components/DataInput';
import HealthGauge, { MetricsGrid } from './components/HealthGauge';
import { ProfitChart, SurvivalChart } from './components/Charts';
import { RiskCards, RoadmapCards } from './components/InsightCards';
import './App.css';

export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleReset = () => setResult(null);

  return (
    <div className="app-container">
      {/* Hero / Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-group" onClick={result ? handleReset : undefined} style={result ? { cursor: 'pointer' } : {}}>
            {result && <ArrowLeft size={18} style={{ opacity: 0.6, marginRight: 4 }} />}
            <div className="logo-icon">
              <Activity size={20} />
            </div>
            <div>
              <h1 className="logo-text">FinTwin</h1>
              <p className="logo-sub">MSME Stress Simulator</p>
            </div>
          </div>
          {result && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="header-badge">
              <Clock size={12} /> {result.elapsed_seconds}s
            </motion.div>
          )}
        </div>
      </header>

      <main className="main-content">
        <AnimatePresence mode="wait">
          {!result && !loading ? (
            <motion.div
              key="input"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -30 }}
              transition={{ duration: 0.3 }}
              className="hero-section"
            >
              <div className="hero-text">
                <h2>
                  Financial stress testing
                  <br />
                  <span className="gradient-text">in 30 seconds</span>
                </h2>
                <p>
                  Upload your MSME data or generate synthetic scenarios.
                  Simulate 7 India-specific macroeconomic shocks with Monte Carlo analysis.
                </p>
              </div>
              <DataInput onAnalysisComplete={setResult} setLoading={setLoading} />
            </motion.div>
          ) : loading ? (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="loading-state"
            >
              <div className="loading-spinner" />
              <p>Running Monte Carlo simulation...</p>
              <p className="loading-sub">Analyzing 7 shock scenarios</p>
            </motion.div>
          ) : (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
            >
              {/* Metrics Row */}
              <section className="section">
                <div className="section-title">
                  <BarChart3 size={18} className="icon" /> Financial Overview
                </div>
                <MetricsGrid metrics={result.metrics} />
              </section>

              {/* Gauge + Profit Chart */}
              <section className="section">
                <div className="dashboard-grid-2">
                  <div>
                    <div className="section-title">
                      <Activity size={18} className="icon" /> Health Score
                    </div>
                    <HealthGauge health={result.health} />
                  </div>
                  <div>
                    <div className="section-title">
                      <BarChart3 size={18} className="icon" /> Financial Trends
                    </div>
                    <ProfitChart metrics={result.metrics} />
                  </div>
                </div>
              </section>

              {/* Survival Chart */}
              <section className="section">
                <div className="section-title">
                  <Zap size={18} className="icon" /> Stress Test Results
                </div>
                <SurvivalChart simulations={result.simulations} />
              </section>

              {/* Risks + Roadmap */}
              <section className="section">
                <div className="dashboard-grid-2">
                  <div>
                    <div className="section-title">
                      <AlertTriangle size={18} className="icon" /> Top Risks
                    </div>
                    <RiskCards risks={result.risks} />
                  </div>
                  <div>
                    <div className="section-title">
                      <Map size={18} className="icon" /> Financial Roadmap
                    </div>
                    <RoadmapCards roadmap={result.roadmap} />
                  </div>
                </div>
              </section>

              {/* New Analysis */}
              <div style={{ textAlign: 'center', marginTop: '2rem', paddingBottom: '3rem' }}>
                <button className="btn btn-secondary" onClick={handleReset}>
                  <ArrowLeft size={14} /> New Analysis
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
