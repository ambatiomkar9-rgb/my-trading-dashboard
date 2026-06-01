import React, { useEffect, useMemo, useState } from 'react';
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

const API_URL = '';

interface Strategy {
  id: string;
  name: string;
  symbol: string;
  timeframe: string;
  status: 'running' | 'paused' | 'backtested';
  pnl: number;
  win_rate: number;
  total_trades: number;
  equity_curve: Array<{ date: string; value: number }>;
  entry_rule?: string;
  exit_rule?: string;
}

interface HermesValidation {
  score: number;
  verdict: string;
  reasoning: string;
  suggestions: string[];
  source: string;
}

interface HermesSuggestion {
  param: string;
  value: number | string;
  reasoning: string;
  source: string;
}

export function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selected, setSelected] = useState<Strategy | null>(null);
  const [showNewForm, setShowNewForm] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newStrategy, setNewStrategy] = useState({
    name: '',
    symbol: 'INFY',
    timeframe: '4h',
    status: 'paused' as 'running' | 'paused' | 'backtested',
    entry_rule: '',
    exit_rule: '',
  });
  const [pineLoading, setPineLoading] = useState(false);
  const [pineScript, setPineScript] = useState('');
  const [pineError, setPineError] = useState<string | null>(null);

  // Hermes state
  const [hermesGenerating, setHermesGenerating] = useState(false);
  const [hermesGenerateResult, setHermesGenerateResult] = useState<any>(null);
  const [hermesGenerateError, setHermesGenerateError] = useState<string | null>(null);
  const [hermesValidating, setHermesValidating] = useState(false);
  const [hermesValidation, setHermesValidation] = useState<HermesValidation | null>(null);
  const [hermesTuning, setHermesTuning] = useState(false);
  const [hermesSuggestion, setHermesSuggestion] = useState<HermesSuggestion | null>(null);
  const [hermesExplaining, setHermesExplaining] = useState(false);
  const [hermesExplanation, setHermesExplanation] = useState<string | null>(null);
  const [hermesAutoGenerating, setHermesAutoGenerating] = useState(false);
  const [hermesStatus, setHermesStatus] = useState<any>(null);

  // Generate form state
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [generateSymbol, setGenerateSymbol] = useState('INFY');
  const [generateTimeframe, setGenerateTimeframe] = useState('1d');

  useEffect(() => {
    fetchStrategies();
    fetchHermesStatus();
  }, []);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  const fetchStrategies = async () => {
    try {
      const res = await fetch(`${API_URL}/strategies`);
      const data = await safeJson(res);
      const list = Array.isArray(data) ? (data as Strategy[]) : [];
      setStrategies(list);
      setSelected(list[0] || null);
    } catch (error) {
      console.error('Error fetching strategies:', error);
      setStrategies([]);
      setSelected(null);
    }
  };

  const fetchHermesStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/strategy/hermes/status`);
      const data = await safeJson(res);
      setHermesStatus(data);
    } catch (error) {
      console.error('Error fetching Hermes status:', error);
    }
  };

  const sortedStrategies = useMemo(() => {
    return [...strategies].sort((a, b) => (b.pnl || 0) - (a.pnl || 0));
  }, [strategies]);

  const handleDelete = async (id: string) => {
    // eslint-disable-next-line no-restricted-globals
    if (!confirm('Delete this strategy?')) return;
    try {
      await fetch(`${API_URL}/strategy/${encodeURIComponent(id)}`, { method: 'DELETE' });
      await fetchStrategies();
      setSelected(null);
    } catch (error) {
      console.error('Error deleting strategy:', error);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const name = newStrategy.name.trim();
    const symbol = newStrategy.symbol.trim().toUpperCase();
    if (!name || !symbol) {
      alert('Name and symbol are required');
      return;
    }
    setCreating(true);
    try {
      const res = await fetch(`${API_URL}/strategy/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          symbol,
          timeframe: newStrategy.timeframe,
          status: newStrategy.status,
          entry_rule: newStrategy.entry_rule,
          exit_rule: newStrategy.exit_rule,
        }),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setShowNewForm(false);
      setNewStrategy({ name: '', symbol: 'INFY', timeframe: '4h', status: 'paused', entry_rule: '', exit_rule: '' });
      await fetchStrategies();
    } catch (err: any) {
      alert(err?.message || 'Failed to create strategy');
    } finally {
      setCreating(false);
    }
  };

  const generatePineScript = async () => {
    if (!selected) return;
    setPineError(null);
    setPineLoading(true);
    setPineScript('');
    try {
      const res = await fetch(`${API_URL}/strategy/pinescript/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: `${selected.name} (${selected.symbol})` }),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setPineScript(String(data?.script || ''));
    } catch (e: any) {
      setPineError(e?.message || 'Failed to generate PineScript');
    } finally {
      setPineLoading(false);
    }
  };

  // ── Hermes Actions ──────────────────────────────────────────────────────

  const hermesGenerate = async () => {
    setHermesGenerating(true);
    setHermesGenerateResult(null);
    setHermesGenerateError(null);
    try {
      const res = await fetch(`${API_URL}/strategy/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ symbol: generateSymbol, timeframe: generateTimeframe }),
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setHermesGenerateResult(data);
      setShowGenerateForm(false);
      await fetchStrategies();
    } catch (e: any) {
      setHermesGenerateError(e?.message || 'Failed to generate strategy');
    } finally {
      setHermesGenerating(false);
    }
  };

  const hermesValidate = async (strategyId: string) => {
    setHermesValidating(true);
    setHermesValidation(null);
    try {
      const res = await fetch(`${API_URL}/strategy/validate/${encodeURIComponent(strategyId)}`, {
        method: 'POST',
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setHermesValidation(data?.validation || null);
    } catch (e: any) {
      console.error('Validation error:', e);
    } finally {
      setHermesValidating(false);
    }
  };

  const hermesTune = async (strategyId: string) => {
    setHermesTuning(true);
    setHermesSuggestion(null);
    try {
      const res = await fetch(`${API_URL}/strategy/tune/${encodeURIComponent(strategyId)}`, {
        method: 'POST',
      });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setHermesSuggestion(data?.suggestion || null);
    } catch (e: any) {
      console.error('Tune error:', e);
    } finally {
      setHermesTuning(false);
    }
  };

  const hermesExplain = async (strategyId: string) => {
    setHermesExplaining(true);
    setHermesExplanation(null);
    try {
      const res = await fetch(`${API_URL}/strategy/explain/${encodeURIComponent(strategyId)}`);
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      setHermesExplanation(data?.explanation || 'No explanation available');
    } catch (e: any) {
      console.error('Explain error:', e);
    } finally {
      setHermesExplaining(false);
    }
  };

  const hermesAutoGenerate = async () => {
    setHermesAutoGenerating(true);
    try {
      const res = await fetch(`${API_URL}/strategy/auto-generate`, { method: 'POST' });
      const data = await safeJson(res);
      if (!res.ok) throw new Error(String(data?.detail || data?.raw || `HTTP ${res.status}`));
      alert(data?.message || 'Auto-generation triggered');
      await fetchStrategies();
    } catch (e: any) {
      alert(e?.message || 'Failed to trigger auto-generation');
    } finally {
      setHermesAutoGenerating(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-6">
        <h1 className="text-3xl font-bold">Trading Strategies</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setShowGenerateForm(!showGenerateForm)}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded font-semibold"
          >
            {hermesGenerating ? 'Generating...' : 'Generate with Hermes'}
          </button>
          <button
            onClick={hermesAutoGenerate}
            disabled={hermesAutoGenerating}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-700 rounded font-semibold"
          >
            {hermesAutoGenerating ? 'Auto-Generating...' : 'Auto-Generate'}
          </button>
          <button
            onClick={() => setShowNewForm(!showNewForm)}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded font-semibold"
          >
            + New Strategy
          </button>
        </div>
      </div>

      {/* Hermes Status Banner */}
      {hermesStatus && (
        <div className={`mb-4 p-3 rounded text-sm ${hermesStatus.hermes_available ? 'bg-green-900/50 text-green-400' : 'bg-yellow-900/50 text-yellow-400'}`}>
          Hermes: {hermesStatus.hermes_available ? 'Connected' : 'Offline (fallback mode)'}
          {hermesStatus.hermes_enabled && ' | Strategy generation: enabled'}
        </div>
      )}

      {/* Generate with Hermes Form */}
      {showGenerateForm ? (
        <div className="mb-8 bg-purple-900/30 border border-purple-700 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4 text-purple-400">Generate Strategy with Hermes AI</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-300 mb-2">Symbol</label>
              <input
                value={generateSymbol}
                onChange={(e) => setGenerateSymbol(e.target.value.toUpperCase())}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
                placeholder="INFY"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Timeframe</label>
              <select
                value={generateTimeframe}
                onChange={(e) => setGenerateTimeframe(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
              </select>
            </div>
          </div>
          {hermesGenerateError && <div className="text-red-400 text-sm mt-2">{hermesGenerateError}</div>}
          {hermesGenerateResult && (
            <div className="mt-4 bg-gray-900 rounded p-3">
              <p className="text-green-400 text-sm mb-2">Strategy generated successfully!</p>
              <p className="text-sm text-gray-300">{hermesGenerateResult.explanation}</p>
              <p className="text-xs text-gray-500 mt-1">Confidence: {(hermesGenerateResult.confidence * 100).toFixed(0)}% | Source: {hermesGenerateResult.source}</p>
            </div>
          )}
          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => { setShowGenerateForm(false); setHermesGenerateError(null); setHermesGenerateResult(null); }}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded font-semibold"
            >
              Cancel
            </button>
            <button
              onClick={hermesGenerate}
              disabled={hermesGenerating || !generateSymbol.trim()}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 rounded font-semibold"
            >
              {hermesGenerating ? 'Generating...' : 'Generate'}
            </button>
          </div>
        </div>
      ) : null}

      {/* New Strategy Form */}
      {showNewForm ? (
        <form onSubmit={handleCreate} className="mb-8 bg-gray-900 border border-gray-800 rounded-lg p-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-gray-300 mb-2">Name</label>
              <input
                value={newStrategy.name}
                onChange={(e) => setNewStrategy({ ...newStrategy, name: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
                placeholder="EMA Cross"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Symbol</label>
              <input
                value={newStrategy.symbol}
                onChange={(e) => setNewStrategy({ ...newStrategy, symbol: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
                placeholder="INFY"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Timeframe</label>
              <select
                value={newStrategy.timeframe}
                onChange={(e) => setNewStrategy({ ...newStrategy, timeframe: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-300 mb-2">Status</label>
              <select
                value={newStrategy.status}
                onChange={(e) => setNewStrategy({ ...newStrategy, status: e.target.value as any })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white"
              >
                <option value="paused">paused</option>
                <option value="running">running</option>
                <option value="backtested">backtested</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm text-gray-300 mb-2">Entry Rule / Buy Conditions (text or JSON)</label>
              <textarea
                value={newStrategy.entry_rule}
                onChange={(e) => setNewStrategy({ ...newStrategy, entry_rule: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white min-h-[84px]"
                placeholder='Example: {"rsi":{"below":30},"trend":"bullish"}'
              />
            </div>
            <div className="sm:col-span-2">
              <label className="block text-sm text-gray-300 mb-2">Exit Rule / Sell Conditions (text or JSON)</label>
              <textarea
                value={newStrategy.exit_rule}
                onChange={(e) => setNewStrategy({ ...newStrategy, exit_rule: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-white min-h-[84px]"
                placeholder='Example: {"rsi":{"above":70}}'
              />
            </div>
          </div>

          <div className="mt-4 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowNewForm(false)}
              className="px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded font-semibold"
            >
              {creating ? 'Creating...' : 'Create Strategy'}
            </button>
          </div>
        </form>
      ) : null}

      <section className="mb-8">
        <div className="bg-gray-900 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800">
                <tr>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Symbol</th>
                  <th className="px-4 py-3 text-left">Timeframe</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-right">P&amp;L</th>
                  <th className="px-4 py-3 text-right">Win%</th>
                  <th className="px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {sortedStrategies.map((strat) => (
                  <tr
                    key={strat.id}
                    className={`border-b border-gray-800 cursor-pointer hover:bg-gray-800/60 ${
                      selected?.id === strat.id ? 'bg-gray-800/60' : ''
                    }`}
                    onClick={() => setSelected(strat)}
                  >
                    <td className="px-4 py-3 font-semibold">{strat.name}</td>
                    <td className="px-4 py-3">{strat.symbol}</td>
                    <td className="px-4 py-3">{strat.timeframe}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-1 rounded text-sm ${
                          strat.status === 'running'
                            ? 'bg-green-900 text-green-400'
                            : strat.status === 'paused'
                              ? 'bg-yellow-900 text-yellow-400'
                              : 'bg-gray-800 text-gray-300'
                        }`}
                      >
                        {strat.status}
                      </span>
                    </td>
                    <td className={`px-4 py-3 text-right font-semibold ${strat.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {strat.pnl >= 0 ? '+' : ''}
                      {Number(strat.pnl).toFixed(0)}
                    </td>
                    <td className="px-4 py-3 text-right">{strat.win_rate}%</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDelete(strat.id);
                        }}
                        className="px-2 py-1 bg-red-600 rounded text-sm hover:bg-red-700"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {selected ? (
        <section>
          <h2 className="text-xl font-bold mb-4">Strategy Details: {selected.name}</h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Total Trades</p>
              <p className="text-2xl font-bold">{selected.total_trades}</p>
            </div>
            <div className="bg-gray-900 p-4 rounded">
              <p className="text-gray-400 text-sm">Win Rate</p>
              <p className="text-2xl font-bold text-green-400">{selected.win_rate}%</p>
            </div>
          </div>

          <div className="bg-gray-900 p-4 rounded mb-6">
            <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={selected.equity_curve || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#444" />
                <XAxis dataKey="date" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #444' }} />
                <Line type="monotone" dataKey="value" stroke="#3b82f6" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Hermes Actions */}
          <div className="bg-gray-900 p-4 rounded mb-6">
            <h3 className="text-lg font-semibold mb-4">Hermes AI Actions</h3>
            <div className="flex flex-wrap gap-3 mb-4">
              <button
                onClick={() => hermesValidate(selected.id)}
                disabled={hermesValidating}
                className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-700 rounded text-sm font-semibold"
              >
                {hermesValidating ? 'Validating...' : 'Validate Strategy'}
              </button>
              <button
                onClick={() => hermesTune(selected.id)}
                disabled={hermesTuning}
                className="px-3 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-gray-700 rounded text-sm font-semibold"
              >
                {hermesTuning ? 'Tuning...' : 'Suggest Improvement'}
              </button>
              <button
                onClick={() => hermesExplain(selected.id)}
                disabled={hermesExplaining}
                className="px-3 py-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-gray-700 rounded text-sm font-semibold"
              >
                {hermesExplaining ? 'Explaining...' : 'Explain Strategy'}
              </button>
            </div>

            {/* Validation Result */}
            {hermesValidation && (
              <div className="bg-gray-800 rounded p-3 mb-3">
                <div className="flex items-center gap-3 mb-2">
                  <span className={`px-2 py-1 rounded text-sm font-semibold ${
                    hermesValidation.verdict === 'APPROVED' ? 'bg-green-900 text-green-400' :
                    hermesValidation.verdict === 'REJECTED' ? 'bg-red-900 text-red-400' :
                    'bg-yellow-900 text-yellow-400'
                  }`}>
                    {hermesValidation.verdict}
                  </span>
                  <span className="text-gray-400">Score: {hermesValidation.score}/100</span>
                </div>
                <p className="text-sm text-gray-300">{hermesValidation.reasoning}</p>
                {hermesValidation.suggestions.length > 0 && (
                  <ul className="mt-2 text-xs text-gray-400 list-disc list-inside">
                    {hermesValidation.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                )}
              </div>
            )}

            {/* Tuning Suggestion */}
            {hermesSuggestion && (
              <div className="bg-gray-800 rounded p-3 mb-3">
                <p className="text-sm font-semibold text-orange-400 mb-1">Suggested Change</p>
                <p className="text-sm text-gray-300">
                  Change <code className="bg-gray-700 px-1 rounded">{hermesSuggestion.param}</code> to{' '}
                  <code className="bg-gray-700 px-1 rounded">{String(hermesSuggestion.value)}</code>
                </p>
                <p className="text-xs text-gray-400 mt-1">{hermesSuggestion.reasoning}</p>
              </div>
            )}

            {/* Explanation */}
            {hermesExplanation && (
              <div className="bg-gray-800 rounded p-3">
                <p className="text-sm font-semibold text-cyan-400 mb-1">Strategy Explanation</p>
                <p className="text-sm text-gray-300">{hermesExplanation}</p>
              </div>
            )}
          </div>

          <div className="bg-gray-900 p-4 rounded">
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mb-3">
              <h3 className="text-lg font-semibold">PineScript Generator</h3>
              <button
                onClick={generatePineScript}
                disabled={pineLoading}
                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 rounded text-sm font-semibold"
              >
                {pineLoading ? 'Generating...' : 'Generate PineScript'}
              </button>
            </div>
            {pineError ? <div className="text-red-400 text-sm mb-2">{pineError}</div> : null}
            {pineScript ? (
              <pre className="bg-black/40 border border-gray-800 rounded p-3 text-xs overflow-x-auto whitespace-pre">
                {pineScript}
              </pre>
            ) : (
              <div className="text-gray-400 text-sm">Click "Generate PineScript" to create a starter strategy.</div>
            )}
          </div>
        </section>
      ) : null}
    </div>
  );
}
