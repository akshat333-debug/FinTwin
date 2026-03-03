import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Zap, Database, ArrowRight } from 'lucide-react';
import { analyzeCSV, analyzeSynthetic } from '../services/api';

export default function DataInput({ onAnalysisComplete, setLoading }) {
    const [mode, setMode] = useState('synthetic');
    const [dragOver, setDragOver] = useState(false);
    const [error, setError] = useState(null);

    // Synthetic settings
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
        if (file && file.name.endsWith('.csv')) handleFile(file);
    }, [handleFile]);

    return (
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
            {/* Mode Tabs */}
            <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <button
                    className={`btn btn-sm ${mode === 'upload' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setMode('upload')}
                >
                    <Upload size={14} /> Upload CSV
                </button>
                <button
                    className={`btn btn-sm ${mode === 'synthetic' ? 'btn-primary' : 'btn-secondary'}`}
                    onClick={() => setMode('synthetic')}
                >
                    <Database size={14} /> Synthetic Data
                </button>
            </div>

            <AnimatePresence mode="wait">
                {mode === 'upload' ? (
                    <motion.div
                        key="upload"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                    >
                        <div
                            className={`upload-zone ${dragOver ? 'dragover' : ''}`}
                            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                            onClick={() => document.getElementById('csv-input').click()}
                        >
                            <div className="icon">📄</div>
                            <div className="text">
                                <strong>Drop CSV here</strong> or click to browse
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                                Required: month, revenue, fixed_costs, variable_costs, loan_emi, cash_reserve
                            </div>
                            <input
                                id="csv-input"
                                type="file"
                                accept=".csv"
                                style={{ display: 'none' }}
                                onChange={(e) => handleFile(e.target.files[0])}
                            />
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="synthetic"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                        className="glass-card"
                        style={{ padding: '1.5rem' }}
                    >
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
                            <div>
                                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                                    Business Type
                                </label>
                                <select
                                    className="select-control w-full"
                                    value={businessType}
                                    onChange={(e) => setBusinessType(e.target.value)}
                                >
                                    <option value="stable">🏢 Stable</option>
                                    <option value="growing">📈 Growing</option>
                                    <option value="struggling">📉 Struggling</option>
                                    <option value="seasonal">🎪 Seasonal</option>
                                </select>
                            </div>
                            <div>
                                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                                    Months of Data
                                </label>
                                <select
                                    className="select-control w-full"
                                    value={nMonths}
                                    onChange={(e) => setNMonths(Number(e.target.value))}
                                >
                                    {[6, 9, 12, 18, 24].map(n => <option key={n} value={n}>{n} months</option>)}
                                </select>
                            </div>
                            <div>
                                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                                    Base Revenue (₹)
                                </label>
                                <input
                                    type="number"
                                    className="input-control"
                                    value={baseRevenue}
                                    onChange={(e) => setBaseRevenue(Number(e.target.value))}
                                    step={50000}
                                />
                            </div>
                            <div>
                                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                                    Simulations
                                </label>
                                <select
                                    className="select-control w-full"
                                    value={nSims}
                                    onChange={(e) => setNSims(Number(e.target.value))}
                                >
                                    {[100, 500, 1000, 2000, 5000].map(n => <option key={n} value={n}>{n.toLocaleString()}</option>)}
                                </select>
                            </div>
                        </div>

                        <button className="btn btn-primary w-full" onClick={handleSynthetic}>
                            <Zap size={16} /> Run Stress Analysis <ArrowRight size={14} />
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            {error && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    style={{
                        marginTop: '1rem',
                        padding: '0.75rem 1rem',
                        background: 'rgba(244, 63, 94, 0.1)',
                        border: '1px solid rgba(244, 63, 94, 0.3)',
                        borderRadius: 'var(--radius-md)',
                        color: '#f43f5e',
                        fontSize: '0.85rem',
                    }}
                >
                    {error}
                </motion.div>
            )}
        </div>
    );
}
