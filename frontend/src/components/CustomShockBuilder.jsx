import { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Zap, Play, ArrowRight, Minus, Plus, Info } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const PRESET_SHOCKS = [
    { label: 'Client Loss', revenue: -0.40, expense: 0, cash: 0, months: 6 },
    { label: 'Raw Material Spike', revenue: 0, expense: 0.25, cash: 0, months: null },
    { label: 'Supply Chain Break', revenue: -0.20, expense: 0.10, cash: -0.15, months: 3 },
    { label: 'Regulatory Fine', revenue: 0, expense: 0, cash: -0.30, months: null },
];

export default function CustomShockBuilder({ onResult }) {
    const [shockName, setShockName] = useState('');
    const [revenueImpact, setRevenueImpact] = useState(0);
    const [expenseImpact, setExpenseImpact] = useState(0);
    const [cashImpact, setCashImpact] = useState(0);
    const [durationMonths, setDurationMonths] = useState(null);
    const [nSims, setNSims] = useState(1000);
    const [businessType, setBusinessType] = useState('stable');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const applyPreset = (preset) => {
        setShockName(preset.label);
        setRevenueImpact(preset.revenue);
        setExpenseImpact(preset.expense);
        setCashImpact(preset.cash);
        setDurationMonths(preset.months);
    };

    const handleRun = useCallback(async () => {
        if (!shockName.trim()) {
            setError('Please name your shock scenario');
            return;
        }
        setError(null);
        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/custom-shock`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    shock_name: shockName,
                    revenue_impact: revenueImpact,
                    expense_impact: expenseImpact,
                    cash_reserve_impact: cashImpact,
                    duration_months: durationMonths,
                    n_simulations: nSims,
                    business_type: businessType,
                }),
            });
            if (!res.ok) throw new Error('Simulation failed');
            const data = await res.json();
            setResult(data);
            if (onResult) onResult(data);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [shockName, revenueImpact, expenseImpact, cashImpact, durationMonths, nSims, businessType, onResult]);

    const survivalColor = (pct) => {
        if (pct >= 80) return 'var(--success)';
        if (pct >= 60) return '#69f0ae';
        if (pct >= 40) return 'var(--warning)';
        if (pct >= 20) return '#ff6e40';
        return 'var(--danger)';
    };

    return (
        <div>
            <div className="card" style={{ marginBottom: '1rem' }}>
                <div className="card-header">
                    <span className="card-title"><Zap size={16} className="icon" /> Custom Shock Builder</span>
                </div>
                <div className="card-body">
                    {/* Presets */}
                    <div style={{ marginBottom: '1.25rem' }}>
                        <div style={{ fontSize: '0.72rem', textTransform: 'uppercase', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                            Quick Presets
                        </div>
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                            {PRESET_SHOCKS.map(p => (
                                <button
                                    key={p.label}
                                    className="btn btn-outline btn-sm"
                                    onClick={() => applyPreset(p)}
                                    style={{ fontSize: '0.78rem' }}
                                >
                                    {p.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Form */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                        <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                            <label className="form-label">Shock Name</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder='e.g. "Biggest client leaves"'
                                value={shockName}
                                onChange={(e) => setShockName(e.target.value)}
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">
                                Revenue Impact: <strong style={{ color: revenueImpact < 0 ? 'var(--danger)' : 'var(--success)' }}>{(revenueImpact * 100).toFixed(0)}%</strong>
                            </label>
                            <input
                                type="range" min={-100} max={50} value={revenueImpact * 100}
                                onChange={(e) => setRevenueImpact(Number(e.target.value) / 100)}
                                className="form-range"
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                                <span>-100% (total loss)</span><span>+50%</span>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">
                                Expense Impact: <strong style={{ color: expenseImpact > 0 ? 'var(--warning)' : 'var(--success)' }}>+{(expenseImpact * 100).toFixed(0)}%</strong>
                            </label>
                            <input
                                type="range" min={0} max={100} value={expenseImpact * 100}
                                onChange={(e) => setExpenseImpact(Number(e.target.value) / 100)}
                                className="form-range"
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                                <span>0%</span><span>+100%</span>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">
                                Cash Reserve Hit: <strong style={{ color: cashImpact < 0 ? 'var(--danger)' : 'var(--text-secondary)' }}>{(cashImpact * 100).toFixed(0)}%</strong>
                            </label>
                            <input
                                type="range" min={-100} max={0} value={cashImpact * 100}
                                onChange={(e) => setCashImpact(Number(e.target.value) / 100)}
                                className="form-range"
                            />
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                                <span>-100%</span><span>0% (no change)</span>
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Duration (months)</label>
                            <select className="form-select" value={durationMonths || 'all'} onChange={(e) => setDurationMonths(e.target.value === 'all' ? null : Number(e.target.value))}>
                                <option value="all">All months</option>
                                {[1, 2, 3, 4, 6, 9, 12].map(n => <option key={n} value={n}>{n} months</option>)}
                            </select>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Business Type</label>
                            <select className="form-select" value={businessType} onChange={(e) => setBusinessType(e.target.value)}>
                                <option value="stable">🏢 Stable</option>
                                <option value="growing">📈 Growing</option>
                                <option value="struggling">📉 Struggling</option>
                                <option value="seasonal">🎪 Seasonal</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Simulations</label>
                            <select className="form-select" value={nSims} onChange={(e) => setNSims(Number(e.target.value))}>
                                {[100, 500, 1000, 2000, 5000].map(n => <option key={n} value={n}>{n.toLocaleString()}</option>)}
                            </select>
                        </div>
                    </div>

                    <button className="btn btn-primary btn-block btn-lg" onClick={handleRun} disabled={loading}>
                        {loading ? (
                            <><span className="spinner-sm" /> Running Simulation...</>
                        ) : (
                            <><Play size={16} /> Run Custom Shock <ArrowRight size={14} /></>
                        )}
                    </button>
                </div>
            </div>

            {error && (
                <div style={{ padding: '0.65rem 1rem', background: 'var(--danger-bg)', border: '1px solid var(--danger)', borderRadius: 'var(--radius)', color: 'var(--danger)', fontSize: '0.82rem', marginBottom: '1rem' }}>
                    {error}
                </div>
            )}

            {/* Result card */}
            {result && (
                <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="card">
                    <div className="card-header">
                        <span className="card-title"><Zap size={16} className="icon" /> Result: {result.shock_name}</span>
                    </div>
                    <div className="card-body" style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: '3rem', fontWeight: 800, color: survivalColor(result.survival_percentage), marginBottom: '0.5rem' }}>
                            {result.survival_percentage.toFixed(1)}%
                        </div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                            Survival Probability
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', fontSize: '0.8rem' }}>
                            <div>
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Survived</div>
                                <div style={{ fontWeight: 700, color: 'var(--success)' }}>{result.survived_count.toLocaleString()}</div>
                            </div>
                            <div>
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Failed</div>
                                <div style={{ fontWeight: 700, color: 'var(--danger)' }}>{result.failed_count.toLocaleString()}</div>
                            </div>
                            <div>
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Avg Months</div>
                                <div style={{ fontWeight: 700 }}>{result.avg_months_survived.toFixed(1)}</div>
                            </div>
                        </div>
                    </div>
                </motion.div>
            )}
        </div>
    );
}
