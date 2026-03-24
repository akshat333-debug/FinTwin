import { NavLink } from 'react-router-dom';
import { Activity, BarChart3, Upload, Zap, FileText, Database, Shield, Landmark, TrendingUp, History, Crosshair } from 'lucide-react';

const NAV_SECTIONS = [
    {
        label: 'Main',
        items: [
            { path: '/', label: 'Dashboard', icon: BarChart3 },
            { path: '/upload', label: 'Upload CSV', icon: Upload },
            { path: '/synthetic', label: 'Synthetic Data', icon: Database },
        ],
    },
    {
        label: 'Analysis',
        items: [
            { path: '/forecast', label: 'Cash Flow Forecast', icon: TrendingUp },
            { path: '/backtest', label: 'Historical Backtest', icon: History },
            { path: '/schemes', label: 'Govt Schemes', icon: Landmark },
            { path: '/risks', label: 'Risk Analysis', icon: Shield },
            { path: '/shocks', label: 'Shock Models', icon: Zap },
            { path: '/custom-shock', label: 'Custom Shock', icon: Crosshair },
        ],
    },
    {
        label: 'System',
        items: [
            { path: '/docs', label: 'CSV Schema', icon: FileText },
        ],
    },
];

export default function Sidebar() {
    return (
        <aside className="sidebar">
            {/* Brand */}
            <div className="sidebar-brand">
                <div className="sidebar-brand-icon">
                    <Activity size={16} />
                </div>
                <div>
                    <div className="sidebar-brand-text">FinTwin</div>
                    <div className="sidebar-brand-sub">Stress Simulator</div>
                </div>
            </div>

            {/* Navigation */}
            <nav className="sidebar-nav">
                {NAV_SECTIONS.map(section => (
                    <div key={section.label}>
                        <div className="sidebar-section-label">{section.label}</div>
                        {section.items.map(item => {
                            const Icon = item.icon;
                            return (
                                <NavLink
                                    key={item.path}
                                    to={item.path}
                                    end={item.path === '/'}
                                    className={({ isActive }) => `sidebar-item ${isActive ? 'active' : ''}`}
                                >
                                    <Icon className="icon" size={18} />
                                    {item.label}
                                </NavLink>
                            );
                        })}
                    </div>
                ))}
            </nav>

            {/* Footer */}
            <div className="sidebar-footer">
                <div style={{ fontSize: '0.68rem', color: 'var(--text-sidebar)', padding: '0.25rem 0.5rem' }}>
                    v3.2 — Hackathon Edition
                </div>
            </div>
        </aside>
    );
}
