import { Component } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

/**
 * Error Boundary component that catches render errors in child components
 * and displays a fallback UI instead of crashing the whole dashboard.
 */
export default class ErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, info) {
        console.error(`[ErrorBoundary] ${this.props.name || 'Component'} crashed:`, error, info);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
                    <AlertTriangle size={28} style={{ color: 'var(--warning)', marginBottom: '0.75rem' }} />
                    <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>
                        {this.props.name || 'Component'} encountered an error
                    </h3>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                        {this.state.error?.message || 'Something went wrong rendering this section.'}
                    </p>
                    <button
                        className="btn btn-outline btn-sm"
                        onClick={() => this.setState({ hasError: false, error: null })}
                    >
                        <RefreshCw size={13} /> Retry
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}
