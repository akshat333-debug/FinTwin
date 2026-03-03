import { motion } from 'framer-motion';
import { AlertTriangle, Shield, TrendingDown, DollarSign, Clock, ArrowRight } from 'lucide-react';

const severityBadge = {
    Critical: 'badge-danger',
    High: 'badge-warning',
    Medium: 'badge-info',
    Low: 'badge-success',
};
const severityIcon = {
    Critical: AlertTriangle,
    High: TrendingDown,
    Medium: Shield,
    Low: DollarSign,
};

export function RiskCards({ risks }) {
    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title"><AlertTriangle size={16} className="icon" /> Risk Analysis</span>
                <span className="badge badge-danger">{risks.length} identified</span>
            </div>
            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {risks.map((risk, i) => {
                    const Icon = severityIcon[risk.severity] || Shield;
                    return (
                        <motion.div key={i}
                            initial={{ opacity: 0, x: -15 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.3 + i * 0.08 }}
                            style={{
                                padding: '1rem',
                                background: 'var(--bg-secondary)',
                                borderRadius: 'var(--radius)',
                                border: '1px solid var(--border-light)',
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
                                <Icon size={15} style={{ color: risk.severity === 'Critical' ? 'var(--danger)' : risk.severity === 'High' ? 'var(--warning)' : 'var(--info)' }} />
                                <span style={{ fontWeight: 600, fontSize: '0.85rem', flex: 1 }}>{risk.risk_name}</span>
                                <span className={`badge ${severityBadge[risk.severity]}`}>{risk.severity}</span>
                            </div>
                            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.4rem' }}>
                                {risk.explanation}
                            </p>
                            <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                📊 {risk.evidence}
                            </p>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}

const categoryColors = {
    'Cash Management': 'var(--primary)',
    'Risk Mitigation': 'var(--warning)',
    'Revenue Growth': 'var(--success)',
    'Cost Reduction': 'var(--danger)',
    'Operational Efficiency': 'var(--info)',
};

export function RoadmapCards({ roadmap }) {
    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title"><ArrowRight size={16} className="icon" /> Action Roadmap</span>
                <span className="badge badge-primary">{roadmap.length} actions</span>
            </div>
            <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {roadmap.map((action, i) => {
                    const catColor = categoryColors[action.category] || 'var(--primary)';
                    return (
                        <motion.div key={i}
                            initial={{ opacity: 0, x: 15 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: 0.4 + i * 0.08 }}
                            style={{
                                padding: '1rem',
                                background: 'var(--bg-secondary)',
                                borderRadius: 'var(--radius)',
                                border: '1px solid var(--border-light)',
                                borderLeft: `3px solid ${catColor}`,
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                    <span style={{
                                        width: 22, height: 22, borderRadius: 'var(--radius-full)',
                                        background: catColor, color: 'white',
                                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: '0.65rem', fontWeight: 700,
                                    }}>
                                        {action.priority}
                                    </span>
                                    <span style={{ fontSize: '0.68rem', fontWeight: 600, color: catColor, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                                        {action.category}
                                    </span>
                                </div>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                    <Clock size={11} /> {action.timeline}
                                </span>
                            </div>
                            <p style={{ fontSize: '0.85rem', fontWeight: 600, lineHeight: 1.5, marginBottom: '0.35rem' }}>
                                {action.action}
                            </p>
                            <p style={{ fontSize: '0.75rem', color: 'var(--success)' }}>
                                💡 {action.impact}
                            </p>
                        </motion.div>
                    );
                })}
            </div>
        </div>
    );
}
