import { Activity, BarChart3, Upload, Zap, Settings, FileText, Database, Shield } from 'lucide-react';

const NAV_SECTIONS = [
    {
        label: 'Main',
        items: [
            { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
            { id: 'upload', label: 'Upload CSV', icon: Upload },
            { id: 'synthetic', label: 'Synthetic Data', icon: Database },
        ],
    },
    {
        label: 'Analysis',
        items: [
            { id: 'shocks', label: 'Shock Models', icon: Zap },
            { id: 'risks', label: 'Risk Analysis', icon: Shield },
        ],
    },
    {
        label: 'System',
        items: [
            { id: 'docs', label: 'CSV Schema', icon: FileText },
        ],
    },
];

export default function Sidebar({ activePage, onNavigate }) {
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
                                <button
                                    key={item.id}
                                    className={`sidebar-item ${activePage === item.id ? 'active' : ''}`}
                                    onClick={() => onNavigate(item.id)}
                                >
                                    <Icon className="icon" size={18} />
                                    {item.label}
                                </button>
                            );
                        })}
                    </div>
                ))}
            </nav>

            {/* Footer */}
            <div className="sidebar-footer">
                <div style={{ fontSize: '0.68rem', color: 'var(--text-sidebar)', padding: '0.25rem 0.5rem' }}>
                    v2.0 — 79 Tests Passing
                </div>
            </div>
        </aside>
    );
}
