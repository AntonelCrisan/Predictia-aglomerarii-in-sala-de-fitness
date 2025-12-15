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
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h1>Ceva nu a mers bine</h1>
          <p>A apărut o eroare în aplicație. Te rugăm să reîncarci pagina.</p>
          <button onClick={() => window.location.reload()}>Reîncarca pagina</button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;