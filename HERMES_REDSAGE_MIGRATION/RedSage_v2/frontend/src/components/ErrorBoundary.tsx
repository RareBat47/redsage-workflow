import React, { Component, ErrorInfo, ReactNode } from 'react';

type Props = { children: ReactNode };
type State = { hasError: boolean; error?: Error };

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('Uncaught UI exception', error, info);
  }

  render() {
    if (!this.state.hasError) return this.props.children;
    return <main className="error-boundary" role="alert">
      <h1>Workspace Display Error</h1>
      <p>Your project state and evidence on disk are safe.</p>
      <button onClick={() => window.location.reload()}>Reload Workspace</button>
    </main>;
  }
}
