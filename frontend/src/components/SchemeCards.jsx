import { motion } from 'framer-motion';
import { ExternalLink, Star } from 'lucide-react';

const urgencyBadge = {
    Critical: 'badge-danger',
    High: 'badge-warning',
    Medium: 'badge-info',
    Low: 'badge-success',
};

export default function SchemeCards({ schemes }) {
    if (!schemes?.length) return null;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {schemes.map((scheme, i) => (
                <motion.div key={scheme.id} className="card"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.06 }}
                >
                    <div style={{ padding: '1.25rem' }}>
                        {/* Header row */}
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flex: 1 }}>
                                <span style={{ fontSize: '1.4rem' }}>{scheme.icon}</span>
                                <div>
                                    <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>{scheme.name}</div>
                                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{scheme.category}</div>
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                                <span className={`badge ${urgencyBadge[scheme.urgency]}`}>{scheme.urgency}</span>
                                <span className="badge badge-primary" style={{ gap: '0.2rem' }}>
                                    <Star size={10} /> {scheme.relevance_score}%
                                </span>
                            </div>
                        </div>

                        {/* Description */}
                        <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.5rem' }}>
                            {scheme.description}
                        </p>

                        {/* Reason */}
                        <div style={{
                            padding: '0.6rem 0.8rem',
                            background: 'var(--primary-bg)',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.78rem',
                            color: 'var(--primary)',
                            marginBottom: '0.75rem',
                            lineHeight: 1.5,
                        }}>
                            💡 {scheme.reason}
                        </div>

                        {/* Details row */}
                        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
                            <div>
                                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'block' }}>Max Amount</span>
                                <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>{scheme.max_amount}</span>
                            </div>
                            <div>
                                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'block' }}>Interest/Subsidy</span>
                                <span style={{ fontSize: '0.82rem', fontWeight: 600 }}>{scheme.interest}</span>
                            </div>
                            <div style={{ flex: 1 }}>
                                <span style={{ fontSize: '0.68rem', color: 'var(--text-muted)', display: 'block' }}>Eligibility</span>
                                <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{scheme.eligibility}</span>
                            </div>
                            <a href={scheme.url} target="_blank" rel="noopener noreferrer"
                                className="btn btn-outline btn-sm"
                                style={{ textDecoration: 'none' }}>
                                <ExternalLink size={12} /> Apply
                            </a>
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
}
