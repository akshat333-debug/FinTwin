import { useTheme } from './ThemeProvider';
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    ComposedChart, Line, CartesianGrid, Area, Cell, ReferenceLine,
} from 'recharts';
import { formatINR } from '../services/api';

function ChartTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null;
    return (
        <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border)',
            borderRadius: 'var(--radius)',
            padding: '0.6rem 0.8rem',
            fontSize: '0.75rem',
            boxShadow: 'var(--shadow-md)',
        }}>
            <div style={{ color: 'var(--text-muted)', marginBottom: '0.3rem', fontWeight: 500 }}>{label}</div>
            {payload.map((p, i) => (
                <div key={i} style={{ display: 'flex', gap: '0.5rem', justifyContent: 'space-between', color: p.color }}>
                    <span>{p.name}:</span>
                    <span style={{ fontWeight: 600 }}>{typeof p.value === 'number' ? formatINR(p.value) : p.value}</span>
                </div>
            ))}
        </div>
    );
}

export function ProfitChart({ metrics }) {
    const { theme } = useTheme();
    const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)';
    const axisColor = theme === 'dark' ? '#475569' : '#94a3b8';

    const data = metrics.months.map((month, i) => ({
        month: month.substring(5),
        revenue: metrics.revenues[i],
        profit: metrics.monthly_profit[i],
    }));

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Revenue & Profit Trend</span>
            </div>
            <div className="card-body">
                <ResponsiveContainer width="100%" height={260}>
                    <ComposedChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                        <XAxis dataKey="month" tick={{ fill: axisColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} />
                        <YAxis tick={{ fill: axisColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickFormatter={v => formatINR(v)} />
                        <Tooltip content={<ChartTooltip />} />
                        <ReferenceLine y={0} stroke={gridColor} />
                        <Area type="monotone" dataKey="revenue" fill="var(--primary-bg)" stroke="none" />
                        <Line type="monotone" dataKey="revenue" stroke="var(--chart-1)" strokeWidth={2}
                            dot={{ fill: 'var(--chart-1)', r: 3, strokeWidth: 0 }} name="Revenue" />
                        <Bar dataKey="profit" name="Profit" radius={[3, 3, 0, 0]} barSize={20}>
                            {data.map((entry, i) => (
                                <Cell key={i}
                                    fill={entry.profit >= 0 ? 'var(--success)' : 'var(--danger)'}
                                    fillOpacity={0.2}
                                    stroke={entry.profit >= 0 ? 'var(--success)' : 'var(--danger)'}
                                    strokeWidth={1}
                                />
                            ))}
                        </Bar>
                    </ComposedChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}

export function SurvivalChart({ simulations }) {
    const { theme } = useTheme();
    const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)';
    const axisColor = theme === 'dark' ? '#475569' : '#94a3b8';

    const data = [...simulations]
        .sort((a, b) => a.survival_percentage - b.survival_percentage)
        .map(s => ({
            name: s.shock_name,
            survival: s.survival_percentage,
        }));

    const getColor = (pct) => {
        if (pct >= 80) return 'var(--success)';
        if (pct >= 60) return 'var(--info)';
        if (pct >= 40) return 'var(--warning)';
        if (pct >= 20) return '#f97316';
        return 'var(--danger)';
    };

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Survival Probability by Shock</span>
                <span className="badge badge-primary">{simulations.length} scenarios</span>
            </div>
            <div className="card-body">
                <ResponsiveContainer width="100%" height={280}>
                    <BarChart data={data} layout="vertical" margin={{ top: 0, right: 30, bottom: 0, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} horizontal={false} />
                        <XAxis type="number" domain={[0, 100]}
                            tick={{ fill: axisColor, fontSize: 11 }} axisLine={{ stroke: gridColor }}
                            tickFormatter={v => `${v}%`} />
                        <YAxis type="category" dataKey="name" width={120}
                            tick={{ fill: axisColor, fontSize: 11 }} axisLine={false} tickLine={false} />
                        <Tooltip content={({ active, payload }) => {
                            if (!active || !payload?.length) return null;
                            const d = payload[0].payload;
                            return (
                                <div style={{
                                    background: 'var(--bg-card)', border: '1px solid var(--border)',
                                    borderRadius: 'var(--radius)', padding: '0.5rem 0.7rem', fontSize: '0.75rem',
                                    boxShadow: 'var(--shadow-md)',
                                }}>
                                    <div style={{ fontWeight: 600 }}>{d.name}</div>
                                    <div style={{ color: getColor(d.survival) }}>Survival: {d.survival.toFixed(1)}%</div>
                                </div>
                            );
                        }} />
                        <Bar dataKey="survival" radius={[0, 4, 4, 0]} barSize={16}>
                            {data.map((entry, i) => (
                                <Cell key={i} fill={getColor(entry.survival)} fillOpacity={0.7} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
