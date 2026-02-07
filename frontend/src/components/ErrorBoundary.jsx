import React from 'react';

class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true };
    }

    componentDidCatch(error, errorInfo) {
        console.error("ErrorBoundary caught an error", error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '20px', textAlign: 'center', color: 'red' }}>
                    <h1>Something went wrong.</h1>
                    <p>Please refresh the page or try again.</p>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
