import { motion } from 'framer-motion';
import { AlertTriangle, Shield, TrendingDown, DollarSign } from 'lucide-react';

const severityConfig = {
    Critical: { color: '#f43f5e', bg: 'rgba(244,63,94,0.06)', border: 'rgba(244,63,94,0.2)', icon: AlertTriangle },
    High: { color: '#f97316', bg: 'rgba(249,115,22,0.06)', border: 'rgba(249,115,22,0.2)', icon: TrendingDown },
    Medium: { color: '#06b6d4', bg: 'rgba(6,182,212,0.06)', border: 'rgba(6,182,212,0.2)', icon: Shield },
    Low: { color: '#10b981', bg: 'rgba(16,185,129,0.06)', border: 'rgba(16,185,129,0.2)', icon: DollarSign },
};

export function RiskCards({ risks }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {risks.map((risk, i) => {
                const config = severityConfig[risk.severity] || severityConfig.Medium;
                const Icon = config.icon;
                return (
                    <motion.div
                        key={i}
                        className="glass-card"
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 + i * 0.1 }}
                        style={{
                            padding: '1.25rem',
                            borderLeft: `3px solid ${config.color}`,
                            background: config.bg,
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                            <div style={{
                                width: 32, height: 32, borderRadius: 'var(--radius-sm)',
                                background: `${config.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>
                                <Icon size={16} color={config.color} />
                            </div>
                            <div style={{ flex: 1 }}>
                                <span style={{ fontWeight: 700, fontSize: '0.9rem' }}>{risk.risk_name}</span>
                            </div>
                            <span className={`badge badge-${risk.severity.toLowerCase()}`}>{risk.severity}</span>
                        </div>
                        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.5rem' }}>
                            {risk.explanation}
                        </p>
                        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontStyle: 'italic' }}>
                            📊 {risk.evidence}
                        </p>
                    </motion.div>
                );
            })}
        </div>
    );
}

const categoryColors = {
    'Cash Management': '#6366f1',
    'Risk Mitigation': '#f59e0b',
    'Revenue Growth': '#10b981',
    'Cost Reduction': '#f43f5e',
    'Operational Efficiency': '#06b6d4',
};

export function RoadmapCards({ roadmap }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {roadmap.map((action, i) => {
                const catColor = categoryColors[action.category] || 'var(--accent-indigo)';
                return (
                    <motion.div
                        key={i}
                        className="glass-card"
                        initial={{ opacity: 0, x: 30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 + i * 0.1 }}
                        style={{
                            padding: '1.25rem',
                            borderLeft: `3px solid ${catColor}`,
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.6rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <span style={{
                                    width: 24, height: 24, borderRadius: 'var(--radius-full)',
                                    background: `${catColor}25`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                                    fontSize: '0.7rem', fontWeight: 800, color: catColor,
                                }}>
                                    {action.priority}
                                </span>
                                <span style={{
                                    fontSize: '0.65rem', color: catColor, fontWeight: 600,
                                    textTransform: 'uppercase', letterSpacing: '0.05em',
                                }}>
                                    {action.category}
                                </span>
                            </div>
                            <span style={{
                                fontSize: '0.7rem', color: 'var(--text-muted)',
                                background: 'rgba(255,255,255,0.04)',
                                padding: '0.15rem 0.5rem', borderRadius: 'var(--radius-full)',
                            }}>
                                ⏱ {action.timeline}
                            </span>
                        </div>
                        <p style={{ fontSize: '0.88rem', fontWeight: 600, marginBottom: '0.4rem', lineHeight: 1.5 }}>
                            {action.action}
                        </p>
                        <p style={{ fontSize: '0.78rem', color: 'var(--accent-emerald)' }}>
                            💡 Impact: {action.impact}
                        </p>
                    </motion.div>
                );
            })}
        </div>
    );
}
