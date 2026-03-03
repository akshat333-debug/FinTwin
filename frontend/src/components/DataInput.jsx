import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Zap, ArrowRight } from 'lucide-react';
import { analyzeCSV, analyzeSynthetic } from '../services/api';

export default function DataInput({ mode = 'synthetic', onAnalysisComplete, setLoading }) {
    const [dragOver, setDragOver] = useState(false);
    const [error, setError] = useState(null);

    const [businessType, setBusinessType] = useState('stable');
    const [nMonths, setNMonths] = useState(12);
    const [baseRevenue, setBaseRevenue] = useState(500000);
    const [nSims, setNSims] = useState(1000);

    const handleFile = useCallback(async (file) => {
        if (!file) return;
        setError(null);
        setLoading(true);
        try {
            const result = await analyzeCSV(file, nSims);
            onAnalysisComplete(result);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [nSims, onAnalysisComplete, setLoading]);

    const handleSynthetic = useCallback(async () => {
        setError(null);
        setLoading(true);
        try {
            const result = await analyzeSynthetic({
                business_type: businessType,
                n_months: nMonths,
                base_revenue: baseRevenue,
                n_simulations: nSims,
            });
            onAnalysisComplete(result);
        } catch (e) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [businessType, nMonths, baseRevenue, nSims, onAnalysisComplete, setLoading]);

    const handleDrop = useCallback((e) => {
        e.preventDefault();
        setDragOver(false);
        const file = e.dataTransfer.files[0];
        if (file?.name.endsWith('.csv')) handleFile(file);
    }, [handleFile]);

    if (mode === 'upload') {
        return (
            <div>
                <div className="card" style={{ marginBottom: '1rem' }}>
                    <div className="card-header">
                        <span className="card-title"><Upload size={16} className="icon" /> Upload Financial Data</span>
                    </div>
                    <div className="card-body">
                        <div
                            className={`upload-zone ${dragOver ? 'dragover' : ''}`}
                            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                            onClick={() => document.getElementById('csv-input').click()}
                        >
                            <Upload size={28} style={{ color: 'var(--text-muted)', marginBottom: '0.75rem' }} />
                            <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '0.25rem' }}>
                                Drop CSV here or click to browse
                            </div>
                            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                                Required: month, revenue, fixed_costs, variable_costs, loan_emi, cash_reserve
                            </div>
                            <input id="csv-input" type="file" accept=".csv" style={{ display: 'none' }}
                                onChange={(e) => handleFile(e.target.files[0])} />
                        </div>
                    </div>
                </div>

                {error && (
                    <div style={{ padding: '0.65rem 1rem', background: 'var(--danger-bg)', border: '1px solid var(--danger)', borderRadius: 'var(--radius)', color: 'var(--danger)', fontSize: '0.82rem' }}>
                        {error}
                    </div>
                )}
            </div>
        );
    }

    // Synthetic mode
    return (
        <div>
            <div className="card" style={{ marginBottom: '1rem' }}>
                <div className="card-header">
                    <span className="card-title"><Zap size={16} className="icon" /> Generate Scenario</span>
                </div>
                <div className="card-body">
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
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
                            <label className="form-label">Duration</label>
                            <select className="form-select" value={nMonths} onChange={(e) => setNMonths(Number(e.target.value))}>
                                {[6, 9, 12, 18, 24].map(n => <option key={n} value={n}>{n} months</option>)}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Base Revenue (₹)</label>
                            <input type="number" className="form-input" value={baseRevenue} onChange={(e) => setBaseRevenue(Number(e.target.value))} step={50000} />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Simulations</label>
                            <select className="form-select" value={nSims} onChange={(e) => setNSims(Number(e.target.value))}>
                                {[100, 500, 1000, 2000, 5000].map(n => <option key={n} value={n}>{n.toLocaleString()}</option>)}
                            </select>
                        </div>
                    </div>

                    <button className="btn btn-primary btn-block btn-lg" onClick={handleSynthetic}>
                        <Zap size={16} /> Run Stress Analysis <ArrowRight size={14} />
                    </button>
                </div>
            </div>

            {error && (
                <div style={{ padding: '0.65rem 1rem', background: 'var(--danger-bg)', border: '1px solid var(--danger)', borderRadius: 'var(--radius)', color: 'var(--danger)', fontSize: '0.82rem' }}>
                    {error}
                </div>
            )}
        </div>
    );
}
