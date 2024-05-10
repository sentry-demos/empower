import React, { Component } from 'react';
import { UnhandledException } from '../utils/errors';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    if (error instanceof UnhandledException) {
      console.error(\"Caught an UnhandledException:\", error);
    } else {
      console.error(\"An unexpected error occurred:\", error);
    }
  }

  render() {
    if (this.state.hasError) {
      return &lt;h1&gt;Something went wrong.&lt;/h1&gt;;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;