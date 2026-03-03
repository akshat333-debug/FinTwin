import { motion } from 'framer-motion';
import { useTheme } from './ThemeProvider';
import { formatINR } from '../services/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';

const severityBadge = {
    Critical: 'badge-danger',
    High: 'badge-warning',
    Medium: 'badge-info',
};

export default function BacktestTimeline({ backtest }) {
    const { theme } = useTheme();
    const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)';
    const axisColor = theme === 'dark' ? '#475569' : '#94a3b8';

    if (!backtest?.length) return null;

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {backtest.map((event, i) => (
                <motion.div key={event.event_id} className="card"
                    initial={{ opacity: 0, y: 15 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.08 }}
                >
                    <div style={{ padding: '1.25rem' }}>
                        {/* Header */}
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                                <span style={{ fontSize: '1.5rem' }}>{event.icon}</span>
                                <div>
                                    <div style={{ fontWeight: 700, fontSize: '0.92rem' }}>{event.event_name}</div>
                                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{event.period} • GDP: {event.gdp_impact}</div>
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: '0.4rem' }}>
                                <span className={`badge ${severityBadge[event.severity]}`}>{event.severity}</span>
                                <span className={`badge ${event.survived ? 'badge-success' : 'badge-danger'}`}>
                                    {event.survived ? '✓ Survived' : '✗ Bankrupt M' + event.bankruptcy_month}
                                </span>
                            </div>
                        </div>

                        {/* Description */}
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.75rem' }}>
                            {event.description}
                        </p>

                        {/* Cash trajectory mini-chart */}
                        <div style={{ marginBottom: '0.75rem' }}>
                            <ResponsiveContainer width="100%" height={140}>
                                <LineChart data={event.trajectory} margin={{ top: 5, right: 10, bottom: 5, left: -10 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                                    <XAxis dataKey="label" tick={{ fill: axisColor, fontSize: 10 }} axisLine={{ stroke: gridColor }} />
                                    <YAxis tick={{ fill: axisColor, fontSize: 10 }} axisLine={{ stroke: gridColor }} tickFormatter={v => formatINR(v)} />
                                    <ReferenceLine y={0} stroke="var(--danger)" strokeDasharray="3 3" strokeOpacity={0.4} />
                                    <Tooltip content={({ active, payload }) => {
                                        if (!active || !payload?.length) return null;
                                        const d = payload[0].payload;
                                        return (
                                            <div style={{
                                                background: 'var(--bg-card)', border: '1px solid var(--border)',
                                                borderRadius: 'var(--radius)', padding: '0.5rem 0.7rem', fontSize: '0.72rem',
                                                boxShadow: 'var(--shadow-md)',
                                            }}>
                                                <div style={{ fontWeight: 600 }}>Month {d.month}</div>
                                                <div>Revenue: {formatINR(d.revenue)} ({d.revenue_change > 0 ? '+' : ''}{d.revenue_change}%)</div>
                                                <div>Cash: <strong style={{ color: d.cash < 0 ? 'var(--danger)' : 'var(--success)' }}>{formatINR(d.cash)}</strong></div>
                                            </div>
                                        );
                                    }} />
                                    <Line type="monotone" dataKey="cash" stroke={event.survived ? 'var(--success)' : 'var(--danger)'}
                                        strokeWidth={2} dot={{ r: 3, fill: event.survived ? 'var(--success)' : 'var(--danger)' }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>

                        {/* Summary row */}
                        <div style={{
                            display: 'flex', gap: '1.5rem', padding: '0.6rem 0.75rem',
                            background: 'var(--bg-secondary)', borderRadius: 'var(--radius)', fontSize: '0.78rem',
                        }}>
                            <div>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem', display: 'block' }}>Final Cash</span>
                                <strong style={{ color: event.final_cash >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                                    {formatINR(event.final_cash)}
                                </strong>
                            </div>
                            <div>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem', display: 'block' }}>Cash Change</span>
                                <strong style={{ color: event.cash_change_pct >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                                    {event.cash_change_pct > 0 ? '+' : ''}{event.cash_change_pct}%
                                </strong>
                            </div>
                            <div>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.65rem', display: 'block' }}>Lowest Cash</span>
                                <strong style={{ color: event.min_cash < 0 ? 'var(--danger)' : 'var(--text-primary)' }}>
                                    {formatINR(event.min_cash)}
                                </strong>
                            </div>
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
}
