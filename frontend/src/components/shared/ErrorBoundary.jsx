import React from 'react';
import './ErrorBoundary.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <div className="error-container">
            <div className="error-icon">⚠️</div>
            <h1>Oops! Something went wrong</h1>
            <p className="error-message">
              We're sorry, but something unexpected happened. The error has been logged
              and we'll look into it.
            </p>
            
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="error-details">
                <summary>Error Details (Development Only)</summary>
                <pre className="error-stack">
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div className="error-actions">
              <button onClick={this.handleReset} className="btn-primary">
                Go to Home
              </button>
              <button onClick={() => window.location.reload()} className="btn-secondary">
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

