import { useTheme } from './ThemeProvider';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from 'recharts';
import { formatINR } from '../services/api';

export default function ForecastChart({ forecast }) {
    const { theme } = useTheme();
    const gridColor = theme === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)';
    const axisColor = theme === 'dark' ? '#475569' : '#94a3b8';

    if (!forecast) return null;

    const data = forecast.months.map((month, i) => ({
        month: month.substring(5),
        p10: forecast.p10[i],
        p25: forecast.p25[i],
        p50: forecast.p50[i],
        p75: forecast.p75[i],
        p90: forecast.p90[i],
    }));

    // Prepend starting point
    data.unshift({
        month: 'Now',
        p10: forecast.starting_cash,
        p25: forecast.starting_cash,
        p50: forecast.starting_cash,
        p75: forecast.starting_cash,
        p90: forecast.starting_cash,
    });

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Cash Flow Forecast (6 Months)</span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                    {forecast.prob_bankrupt_by_end > 0 ? (
                        <span className="badge badge-danger">
                            {(forecast.prob_bankrupt_by_end * 100).toFixed(1)}% bankruptcy risk
                        </span>
                    ) : (
                        <span className="badge badge-success">Low bankruptcy risk</span>
                    )}
                </div>
            </div>
            <div className="card-body">
                {/* Legend */}
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '0.75rem', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    <span>
                        <span style={{ display: 'inline-block', width: 12, height: 3, background: 'var(--chart-1)', borderRadius: 2, marginRight: 4 }}></span>
                        Median (P50)
                    </span>
                    <span>
                        <span style={{ display: 'inline-block', width: 12, height: 8, background: 'var(--primary-bg)', borderRadius: 2, marginRight: 4, opacity: 0.6 }}></span>
                        P25–P75
                    </span>
                    <span>
                        <span style={{ display: 'inline-block', width: 12, height: 8, background: 'var(--primary-bg)', borderRadius: 2, marginRight: 4, opacity: 0.3 }}></span>
                        P10–P90
                    </span>
                </div>

                <ResponsiveContainer width="100%" height={260}>
                    <AreaChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: -10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                        <XAxis dataKey="month" tick={{ fill: axisColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} />
                        <YAxis tick={{ fill: axisColor, fontSize: 11 }} axisLine={{ stroke: gridColor }} tickFormatter={v => formatINR(v)} />
                        <ReferenceLine y={0} stroke="var(--danger)" strokeDasharray="4 4" strokeOpacity={0.5} />

                        <Tooltip content={({ active, payload, label }) => {
                            if (!active || !payload?.length) return null;
                            const d = payload[0]?.payload;
                            if (!d) return null;
                            return (
                                <div style={{
                                    background: 'var(--bg-card)', border: '1px solid var(--border)',
                                    borderRadius: 'var(--radius)', padding: '0.6rem 0.8rem', fontSize: '0.75rem',
                                    boxShadow: 'var(--shadow-md)',
                                }}>
                                    <div style={{ fontWeight: 600, marginBottom: '0.3rem' }}>{label}</div>
                                    <div>Optimistic (P90): <strong>{formatINR(d.p90)}</strong></div>
                                    <div>Expected (P50): <strong>{formatINR(d.p50)}</strong></div>
                                    <div>Pessimistic (P10): <strong style={{ color: d.p10 < 0 ? 'var(--danger)' : undefined }}>{formatINR(d.p10)}</strong></div>
                                </div>
                            );
                        }} />

                        {/* P10-P90 band (outer) */}
                        <Area type="monotone" dataKey="p90" stroke="none" fill="var(--chart-1)" fillOpacity={0.06} />
                        <Area type="monotone" dataKey="p10" stroke="none" fill="var(--bg)" fillOpacity={1} />

                        {/* P25-P75 band (inner) */}
                        <Area type="monotone" dataKey="p75" stroke="none" fill="var(--chart-1)" fillOpacity={0.12} />
                        <Area type="monotone" dataKey="p25" stroke="none" fill="var(--bg)" fillOpacity={1} />

                        {/* Median line */}
                        <Area type="monotone" dataKey="p50" stroke="var(--chart-1)" strokeWidth={2.5}
                            fill="var(--chart-1)" fillOpacity={0.05} dot={{ fill: 'var(--chart-1)', r: 3 }} />
                    </AreaChart>
                </ResponsiveContainer>

                {/* Summary stats */}
                <div style={{
                    display: 'flex', gap: '1.5rem', marginTop: '1rem', padding: '0.75rem',
                    background: 'var(--bg-secondary)', borderRadius: 'var(--radius)', fontSize: '0.78rem',
                }}>
                    <div>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.68rem' }}>Starting Cash</span>
                        <strong>{formatINR(forecast.starting_cash)}</strong>
                    </div>
                    <div>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.68rem' }}>Expected (6mo)</span>
                        <strong style={{ color: forecast.expected_cash_end >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                            {formatINR(forecast.expected_cash_end)}
                        </strong>
                    </div>
                    {forecast.months_to_zero && (
                        <div>
                            <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.68rem' }}>Months to ₹0</span>
                            <strong style={{ color: 'var(--danger)' }}>{forecast.months_to_zero} months</strong>
                        </div>
                    )}
                    <div>
                        <span style={{ color: 'var(--text-muted)', display: 'block', fontSize: '0.68rem' }}>Simulations</span>
                        <strong>{forecast.n_simulations.toLocaleString()}</strong>
                    </div>
                </div>
            </div>
        </div>
    );
}
