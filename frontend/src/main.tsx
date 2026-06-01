import React from 'react'
import ReactDOM from 'react-dom/client'
import AppWrapper from './App.tsx'
import './App.css'
import './index.css'
import { ErrorBoundary } from './components/ErrorBoundary'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <AppWrapper />
    </ErrorBoundary>
  </React.StrictMode>,
)
