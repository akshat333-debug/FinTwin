import { Sun, Moon } from 'lucide-react';
import { useTheme } from './ThemeProvider';

const PAGE_TITLES = {
    dashboard: 'Dashboard',
    upload: 'Upload CSV',
    synthetic: 'Synthetic Data',
    shocks: 'Shock Models',
    risks: 'Risk Analysis',
    docs: 'CSV Schema',
};

export default function TopBar({ activePage }) {
    const { theme, toggle } = useTheme();

    return (
        <div className="topbar">
            <div className="topbar-left">
                <div className="topbar-breadcrumb">
                    FinTwin / <strong>{PAGE_TITLES[activePage] || 'Dashboard'}</strong>
                </div>
            </div>
            <div className="topbar-right">
                <button className="theme-toggle" onClick={toggle} title="Toggle theme">
                    {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
                </button>
            </div>
        </div>
    );
}
