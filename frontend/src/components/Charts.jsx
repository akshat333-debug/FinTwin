import { motion } from 'framer-motion';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    LineChart, Line, CartesianGrid, ComposedChart, Area,
    Cell, ReferenceLine
} from 'recharts';
import { formatINR } from '../services/api';

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div style={{
            background: 'rgba(13,13,31,0.95)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '0.6rem 0.8rem',
            fontSize: '0.75rem',
        }}>
            <div style={{ color: 'var(--text-muted)', marginBottom: '0.3rem' }}>{label}</div>
            {payload.map((p, i) => (
                <div key={i} style={{ color: p.color, display: 'flex', gap: '0.5rem', justifyContent: 'space-between' }}>
                    <span>{p.name}:</span>
                    <span style={{ fontWeight: 600 }}>{typeof p.value === 'number' ? formatINR(p.value) : p.value}</span>
                </div>
            ))}
        </div>
    );
};

export function ProfitChart({ metrics }) {
    const data = metrics.months.map((month, i) => ({
        month: month.substring(5),
        revenue: metrics.revenues[i],
        profit: metrics.monthly_profit[i],
        expenses: metrics.total_expenses[i],
    }));

    return (
        <motion.div
            className="glass-card"
            style={{ padding: '1.25rem' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
        >
            <div className="section-title" style={{ marginBottom: '1rem', fontSize: '1rem' }}>
                Revenue & Profit Trend
            </div>
            <ResponsiveContainer width="100%" height={260}>
                <ComposedChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="month" tick={{ fill: '#5c6080', fontSize: 11 }} axisLine={{ stroke: 'rgba(255,255,255,0.06)' }} />
                    <YAxis tick={{ fill: '#5c6080', fontSize: 11 }} axisLine={{ stroke: 'rgba(255,255,255,0.06)' }} tickFormatter={v => formatINR(v)} />
                    <Tooltip content={<CustomTooltip />} />
                    <ReferenceLine y={0} stroke="rgba(255,255,255,0.1)" strokeDasharray="2 2" />
                    <Area type="monotone" dataKey="revenue" fill="rgba(99,102,241,0.08)" stroke="none" />
                    <Line type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={2} dot={{ fill: '#6366f1', r: 3 }} name="Revenue" />
                    <Bar dataKey="profit" name="Profit" radius={[3, 3, 0, 0]}>
                        {data.map((entry, i) => (
                            <Cell key={i} fill={entry.profit >= 0 ? '#10b98140' : '#f43f5e40'} stroke={entry.profit >= 0 ? '#10b981' : '#f43f5e'} strokeWidth={1} />
                        ))}
                    </Bar>
                </ComposedChart>
            </ResponsiveContainer>
        </motion.div>
    );
}

export function SurvivalChart({ simulations }) {
    const data = [...simulations]
        .sort((a, b) => a.survival_percentage - b.survival_percentage)
        .map(s => ({
            name: s.shock_name,
            survival: s.survival_percentage,
            failed: 100 - s.survival_percentage,
        }));

    const getColor = (pct) => {
        if (pct >= 80) return '#10b981';
        if (pct >= 60) return '#06b6d4';
        if (pct >= 40) return '#f59e0b';
        if (pct >= 20) return '#f97316';
        return '#f43f5e';
    };

    return (
        <motion.div
            className="glass-card"
            style={{ padding: '1.25rem' }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
        >
            <div className="section-title" style={{ marginBottom: '1rem', fontSize: '1rem' }}>
                Survival Probability by Shock
            </div>
            <ResponsiveContainer width="100%" height={280}>
                <BarChart data={data} layout="vertical" margin={{ top: 0, right: 30, bottom: 0, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                    <XAxis type="number" domain={[0, 100]} tick={{ fill: '#5c6080', fontSize: 11 }} axisLine={{ stroke: 'rgba(255,255,255,0.06)' }} tickFormatter={v => `${v}%`} />
                    <YAxis type="category" dataKey="name" width={130} tick={{ fill: '#9ca3c0', fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip content={({ active, payload }) => {
                        if (!active || !payload?.length) return null;
                        const d = payload[0].payload;
                        return (
                            <div style={{ background: 'rgba(13,13,31,0.95)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '0.6rem 0.8rem', fontSize: '0.75rem' }}>
                                <div style={{ fontWeight: 600, marginBottom: '0.2rem' }}>{d.name}</div>
                                <div style={{ color: getColor(d.survival) }}>Survival: {d.survival.toFixed(1)}%</div>
                            </div>
                        );
                    }} />
                    <Bar dataKey="survival" radius={[0, 4, 4, 0]} barSize={18}>
                        {data.map((entry, i) => (
                            <Cell key={i} fill={getColor(entry.survival)} fillOpacity={0.75} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </motion.div>
    );
}
