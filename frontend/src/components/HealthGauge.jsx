import { motion } from 'framer-motion';
import { formatINR, formatPercent } from '../services/api';

const healthColors = {
    Excellent: '#10b981',
    Good: '#06b6d4',
    Fair: '#f59e0b',
    Poor: '#f97316',
    Critical: '#f43f5e',
};

export default function HealthGauge({ health }) {
    const { health_score, grade, interpretation, component_scores } = health;
    const color = healthColors[grade] || '#6366f1';
    const angle = ((health_score - 1) / 9) * 180; // 1-10 mapped to 0-180deg

    return (
        <div className="glass-card" style={{ padding: '1.5rem', textAlign: 'center' }}>
            {/* Gauge SVG */}
            <svg viewBox="0 0 200 120" style={{ width: '100%', maxWidth: 280, margin: '0 auto', display: 'block' }}>
                {/* Background arc */}
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke="rgba(255,255,255,0.06)"
                    strokeWidth="12"
                    strokeLinecap="round"
                />
                {/* Colored arc */}
                <path
                    d="M 20 100 A 80 80 0 0 1 180 100"
                    fill="none"
                    stroke={color}
                    strokeWidth="12"
                    strokeLinecap="round"
                    strokeDasharray={`${(angle / 180) * 251.2} 251.2`}
                    style={{ filter: `drop-shadow(0 0 8px ${color}66)`, transition: 'stroke-dasharray 1s ease' }}
                />
                {/* Needle */}
                <g transform={`rotate(${angle}, 100, 100)`} style={{ transition: 'transform 1s ease' }}>
                    <line x1="100" y1="100" x2="100" y2="35" stroke={color} strokeWidth="2.5" strokeLinecap="round" />
                    <circle cx="100" cy="100" r="5" fill={color} />
                </g>
                {/* Score text */}
                <text x="100" y="88" textAnchor="middle" fill={color} fontSize="28" fontWeight="800" fontFamily="Inter">
                    {health_score}
                </text>
                <text x="100" y="102" textAnchor="middle" fill="rgba(255,255,255,0.5)" fontSize="9" fontFamily="Inter">
                    / 10
                </text>
                {/* Labels */}
                <text x="20" y="115" fill="rgba(255,255,255,0.3)" fontSize="7" fontFamily="Inter">Critical</text>
                <text x="155" y="115" fill="rgba(255,255,255,0.3)" fontSize="7" fontFamily="Inter">Excellent</text>
            </svg>

            {/* Grade badge */}
            <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.3, type: 'spring' }}
                style={{
                    display: 'inline-block',
                    padding: '0.3rem 1rem',
                    borderRadius: 'var(--radius-full)',
                    background: `${color}18`,
                    border: `1px solid ${color}40`,
                    color,
                    fontWeight: 700,
                    fontSize: '0.85rem',
                    marginTop: '0.5rem',
                }}
            >
                {grade}
            </motion.div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.75rem', lineHeight: 1.5 }}>
                {interpretation}
            </p>

            {/* Component bars */}
            <div style={{ marginTop: '1.25rem', textAlign: 'left' }}>
                {Object.entries(component_scores).map(([key, score]) => {
                    const maxScore = key === 'profit_margin' ? 3 : key.includes('burn') || key.includes('cost') ? 1.5 : 2;
                    const pct = (score / maxScore) * 100;
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                    return (
                        <div key={key} style={{ marginBottom: '0.6rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.2rem' }}>
                                <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{label}</span>
                                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>{score}/{maxScore}</span>
                            </div>
                            <div style={{ height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 'var(--radius-full)' }}>
                                <motion.div
                                    initial={{ width: 0 }}
                                    animate={{ width: `${pct}%` }}
                                    transition={{ duration: 0.8, delay: 0.1 }}
                                    style={{ height: '100%', background: color, borderRadius: 'var(--radius-full)' }}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}

export function MetricsGrid({ metrics }) {
    const items = [
        { label: 'Avg Revenue', value: formatINR(metrics.avg_revenue), color: 'var(--accent-indigo)' },
        { label: 'Avg Profit', value: formatINR(metrics.avg_monthly_profit), color: metrics.avg_monthly_profit >= 0 ? 'var(--accent-emerald)' : 'var(--accent-rose)' },
        { label: 'Profit Margin', value: formatPercent(metrics.avg_profit_margin), color: 'var(--accent-cyan)' },
        { label: 'Cash Reserve', value: formatINR(metrics.latest_cash_reserve), color: 'var(--accent-violet)' },
        { label: 'Revenue Volatility', value: formatPercent(metrics.revenue_volatility), color: 'var(--accent-amber)' },
    ];

    return (
        <div className="metric-grid">
            {items.map((item, i) => (
                <motion.div
                    key={item.label}
                    className="glass-card metric-card"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.08 }}
                >
                    <div className="label">{item.label}</div>
                    <div className="value" style={{ background: item.color, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        {item.value}
                    </div>
                </motion.div>
            ))}
        </div>
    );
}
