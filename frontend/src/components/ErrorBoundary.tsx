import React from 'react';

type Props = { children: React.ReactNode };
type State = { hasError: boolean };

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false };

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Frontend error', { error, errorInfo });
    this.setState({ hasError: true });
  }

  render() {
    if (this.state.hasError) {
      return <div style={{ padding: 24, color: '#fff', background: '#111' }}>Something went wrong. Check logs.</div>;
    }
    return this.props.children;
  }
}
