import { motion } from 'framer-motion';
import { formatINR, formatPercent } from '../services/api';
import { TrendingUp, TrendingDown, DollarSign, Wallet, BarChart3, Activity as Pulse } from 'lucide-react';

const healthColors = {
    Excellent: 'var(--success)',
    Good: 'var(--info)',
    Fair: 'var(--warning)',
    Poor: '#f97316',
    Critical: 'var(--danger)',
};

export default function HealthGauge({ health }) {
    const { health_score, grade, interpretation, component_scores } = health;
    const color = healthColors[grade] || 'var(--primary)';
    const pct = ((health_score - 1) / 9) * 100;

    return (
        <div className="card">
            <div className="card-body" style={{ textAlign: 'center', padding: '1.5rem' }}>
                {/* Score circle */}
                <div style={{ position: 'relative', width: 140, height: 140, margin: '0 auto 1rem' }}>
                    <svg viewBox="0 0 140 140" style={{ transform: 'rotate(-90deg)' }}>
                        <circle cx="70" cy="70" r="58" fill="none"
                            stroke="var(--border)" strokeWidth="8" />
                        <motion.circle cx="70" cy="70" r="58" fill="none"
                            stroke={color} strokeWidth="8" strokeLinecap="round"
                            strokeDasharray={`${(pct / 100) * 364.4} 364.4`}
                            initial={{ strokeDasharray: '0 364.4' }}
                            animate={{ strokeDasharray: `${(pct / 100) * 364.4} 364.4` }}
                            transition={{ duration: 1, ease: 'easeOut' }}
                            style={{ filter: `drop-shadow(0 0 6px ${color})` }}
                        />
                    </svg>
                    <div style={{
                        position: 'absolute', top: '50%', left: '50%',
                        transform: 'translate(-50%, -50%)', textAlign: 'center',
                    }}>
                        <div style={{ fontSize: '1.8rem', fontWeight: 800, color }}>{health_score}</div>
                        <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>out of 10</div>
                    </div>
                </div>

                {/* Grade */}
                <span className={`badge ${grade === 'Critical' || grade === 'Poor' ? 'badge-danger' : grade === 'Fair' ? 'badge-warning' : 'badge-success'}`}
                    style={{ fontSize: '0.72rem', padding: '0.25rem 0.7rem' }}>
                    {grade}
                </span>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.75rem', lineHeight: 1.6 }}>
                    {interpretation}
                </p>

                {/* Component bars */}
                <div style={{ marginTop: '1.25rem', textAlign: 'left' }}>
                    {Object.entries(component_scores).map(([key, score]) => {
                        const maxScore = key === 'profit_margin' ? 3 : key.includes('burn') || key.includes('cost') ? 1.5 : 2;
                        const barPct = Math.min((score / maxScore) * 100, 100);
                        const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                        return (
                            <div key={key} style={{ marginBottom: '0.7rem' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                                    <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{label}</span>
                                    <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)' }}>{score.toFixed(1)}</span>
                                </div>
                                <div className="progress-bar">
                                    <motion.div className="progress-fill"
                                        initial={{ width: 0 }}
                                        animate={{ width: `${barPct}%` }}
                                        transition={{ duration: 0.8, delay: 0.1 }}
                                        style={{ background: color }}
                                    />
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}

export function StatCards({ metrics, health }) {
    const items = [
        {
            label: 'Avg Revenue',
            value: formatINR(metrics.avg_revenue),
            icon: DollarSign,
            color: 'var(--primary)',
            bg: 'var(--primary-bg)',
        },
        {
            label: 'Avg Profit',
            value: formatINR(metrics.avg_monthly_profit),
            icon: metrics.avg_monthly_profit >= 0 ? TrendingUp : TrendingDown,
            color: metrics.avg_monthly_profit >= 0 ? 'var(--success)' : 'var(--danger)',
            bg: metrics.avg_monthly_profit >= 0 ? 'var(--success-bg)' : 'var(--danger-bg)',
            change: formatPercent(metrics.avg_profit_margin),
            changeType: metrics.avg_profit_margin >= 0 ? 'positive' : 'negative',
        },
        {
            label: 'Cash Reserve',
            value: formatINR(metrics.latest_cash_reserve),
            icon: Wallet,
            color: 'var(--info)',
            bg: 'var(--info-bg)',
        },
        {
            label: 'Health Score',
            value: `${health.health_score}/10`,
            icon: Pulse,
            color: healthColors[health.grade] || 'var(--primary)',
            bg: health.grade === 'Critical' || health.grade === 'Poor' ? 'var(--danger-bg)' : 'var(--success-bg)',
            change: health.grade,
            changeType: health.grade === 'Critical' || health.grade === 'Poor' ? 'negative' : 'positive',
        },
        {
            label: 'Revenue Volatility',
            value: formatPercent(metrics.revenue_volatility),
            icon: BarChart3,
            color: 'var(--warning)',
            bg: 'var(--warning-bg)',
        },
    ];

    return (
        <div className="stat-grid">
            {items.map((item, i) => {
                const Icon = item.icon;
                return (
                    <motion.div key={item.label} className="card stat-card"
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.06 }}
                    >
                        <div className="stat-icon" style={{ background: item.bg, color: item.color }}>
                            <Icon size={18} />
                        </div>
                        <div className="stat-label">{item.label}</div>
                        <div className="stat-value">{item.value}</div>
                        {item.change && (
                            <div className={`stat-change ${item.changeType}`}>
                                {item.changeType === 'positive' ? '↑' : '↓'} {item.change}
                            </div>
                        )}
                    </motion.div>
                );
            })}
        </div>
    );
}
