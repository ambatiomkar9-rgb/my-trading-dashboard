import React, { useState } from 'react';
import { OverviewPage } from './components/OverviewPage';
import { TradingPage } from './components/TradingPage';
import { StrategiesPage } from './components/StrategiesPage';
import { BacktestingPage } from './components/BacktestingPage';
import { StockScreener } from './components/StockScreener';
import { SettingsPage } from './components/SettingsPage';
import { AgentAnimation } from './components/AgentAnimation';
import { ChatInterface } from './components/ChatInterface';
import { AgentMonitor } from './components/AgentMonitor';
import { WatchlistPage } from './components/WatchlistPage';
import { SignalsPage } from './components/SignalsPage';
import { PortfolioPage } from './components/PortfolioPage';

type Page =
  | 'overview'
  | 'chat'
  | 'watchlist'
  | 'signals'
  | 'portfolio'
  | 'trading'
  | 'strategies'
  | 'backtesting'
  | 'screener'
  | 'settings'
  | 'animation';

function App() {
  const [page, setPage] = useState<Page>('overview');

  const renderPage = () => {
    switch (page) {
      case 'overview': return <OverviewPage />;
      case 'trading': return <TradingPage />;
      case 'strategies': return <StrategiesPage />;
      case 'backtesting': return <BacktestingPage />;
      case 'screener': return <StockScreener />;
      case 'settings': return <SettingsPage />;
      case 'animation': return <AgentAnimation />;
      case 'watchlist': return <WatchlistPage />;
      case 'signals': return <SignalsPage />;
      case 'portfolio': return <PortfolioPage />;
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white grid grid-cols-1 lg:grid-cols-[280px_1fr]">
      <aside className="border-r border-gray-900 p-4">
        <div className="text-lg font-bold mb-3">Trading Dashboard</div>
        <AgentMonitor />
        <div className="h-px bg-gray-800 my-4" />
        <div className="space-y-2">
          {(
            [
              'overview',
              'chat',
              'watchlist',
              'signals',
              'portfolio',
              'trading',
              'strategies',
              'backtesting',
              'screener',
              'settings',
              'animation',
            ] as Page[]
          ).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`w-full text-left px-3 py-2 rounded font-semibold ${
                page === p ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-900 hover:bg-gray-800'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </aside>
      <main className="min-w-0">{renderPage()}</main>
    </div>
  );
}

export default App;
