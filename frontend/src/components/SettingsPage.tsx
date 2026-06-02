import React, { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { api } from '../api';

const API_URL = '';

type Settings = {
  broker?: string;
  api_key?: string;
  api_secret?: string;
  trading_mode?: 'paper' | 'live';
  max_position_size?: number;
  max_daily_loss?: number;
  max_correlation?: number;
  ollama_model?: string;
  ollama_url?: string;
  telegram_enabled?: boolean;
  telegram_bot_token?: string;
  telegram_chat_id?: string;
  hermes_enabled?: boolean;
  hermes_cmd?: string;
  hermes_timeout_sec?: number;
  hermes_poll_interval?: number;
  strategy_gen_interval?: number;
};

export function SettingsPage() {
  const { isAuthenticated, username, logout } = useAuth();
  const [settings, setSettings] = useState<Settings>({
    broker: 'upstox',
    trading_mode: 'paper',
    max_position_size: 5,
    max_daily_loss: 2,
    max_correlation: 0.7,
    ollama_model: 'qwen2.5:3b',
    ollama_url: 'http://localhost:11434',
    telegram_enabled: true,
    telegram_bot_token: '',
    telegram_chat_id: '',
  });

  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);
  const [killEnabled, setKillEnabled] = useState<boolean | null>(null);
  const [adminKey, setAdminKey] = useState<string>(() => localStorage.getItem('admin_api_key') || '');
  const [killBusy, setKillBusy] = useState(false);

  const safeJson = async (res: Response) => {
    const text = await res.text();
    try {
      return text ? JSON.parse(text) : {};
    } catch {
      return { raw: text };
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const data = await api.get('/settings');
        if (data && typeof data === 'object') {
          setSettings((prev) => ({ ...prev, ...data }));
        }

        const ksData = await api.get('/api/kill-switch');
        if (typeof ksData?.trading_enabled === 'boolean') {
          setKillEnabled(ksData.trading_enabled);
        }
      } catch {
        // ignore; keep defaults
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  useEffect(() => {
    localStorage.setItem('admin_api_key', adminKey);
  }, [adminKey]);

  const authHeaders = (): Record<string, string> => {
    if (adminKey) {
      return { 'X-Admin-Key': adminKey };
    }
    return {};
  };

  const toggleKillSwitch = async (enabled: boolean) => {
    setKillBusy(true);
    try {
      const data = await api.post('/api/kill-switch', { enabled });
      setKillEnabled(Boolean(data?.trading_enabled));
    } catch (error) {
      console.error('Kill switch update failed:', error);
      alert('Kill switch update failed (check JWT login / auth settings).');
    } finally {
      setKillBusy(false);
    }
  };

  const handleSave = async () => {
    try {
      await api.post('/settings', settings);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('Error saving settings');
    }
  };

  const handleTestConnection = async () => {
    try {
      const url = `${settings.ollama_url || 'http://localhost:11434'}/api/version`;
      const res = await fetch(url);
      if (res.ok) {
        alert('Ollama connection successful!');
      } else {
        alert('Cannot reach Ollama server from the browser.');
      }
    } catch {
      alert('Connection failed. Note: cloud dashboard cannot reach your local Ollama URL.');
    }
  };

  const handleTelegramTest = async () => {
    try {
      const data = await api.post('/alerts/buy-signal', { symbol: 'TEST', signal: 'buy' });
      alert(`Telegram test: ${data?.status || 'unknown'}`);
    } catch {
      alert('Telegram test failed');
    }
  };

  return (
    <div className="p-6 bg-black text-white">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Settings</h1>
        {loading ? <div className="text-gray-400 text-sm">Loading...</div> : null}
      </div>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Broker API Keys</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Broker</label>
            <select
              value={settings.broker || 'upstox'}
              onChange={(e) => setSettings({ ...settings, broker: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="upstox">Upstox</option>
              <option value="binance">Binance</option>
              <option value="alpaca">Alpaca</option>
            </select>
          </div>
          <div />

          <div>
            <label className="block text-sm mb-2">API Key</label>
            <input
              type="password"
              value={settings.api_key || ''}
              onChange={(e) => setSettings({ ...settings, api_key: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="***masked***"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">API Secret</label>
            <input
              type="password"
              value={settings.api_secret || ''}
              onChange={(e) => setSettings({ ...settings, api_secret: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="***masked***"
            />
          </div>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Trading Mode</h2>
        <div className="space-y-3">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="paper"
              checked={(settings.trading_mode || 'paper') === 'paper'}
              onChange={(e) => setSettings({ ...settings, trading_mode: e.target.value as 'paper' | 'live' })}
            />
            <span>Paper Trading (Safe for testing)</span>
          </label>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              type="radio"
              name="mode"
              value="live"
              checked={(settings.trading_mode || 'paper') === 'live'}
              onChange={(e) => setSettings({ ...settings, trading_mode: e.target.value as 'paper' | 'live' })}
            />
            <span className="text-red-400">LIVE TRADING (Real money)</span>
          </label>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Dashboard Auth</h2>
        <div className="text-sm text-gray-400 mb-3">
          Authentication is handled via the shared auth layer. You are logged in as <strong className="text-white">{username}</strong>.
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-400">
            Status: <span className={isAuthenticated ? 'text-green-400' : 'text-red-400'}>{isAuthenticated ? 'Authenticated' : 'Not authenticated'}</span>
          </div>
          {isAuthenticated && (
            <button onClick={logout} className="px-4 py-2 bg-gray-700 rounded hover:bg-gray-600 text-sm">
              Logout
            </button>
          )}
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Kill Switch</h2>
        <div className="text-sm text-gray-400 mb-3">
          Use the dashboard JWT first. If needed, the legacy `ADMIN_API_KEY` fallback still works.
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Legacy Admin Key (X-Admin-Key)</label>
            <input
              type="password"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="Legacy fallback"
            />
          </div>
          <div className="flex items-end gap-2">
            <button
              disabled={killBusy}
              onClick={() => toggleKillSwitch(true)}
              className="px-4 py-2 bg-green-600 rounded hover:bg-green-700 disabled:bg-gray-700"
            >
              Enable
            </button>
            <button
              disabled={killBusy}
              onClick={() => toggleKillSwitch(false)}
              className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 disabled:bg-gray-700"
            >
              Disable
            </button>
            <div className="text-sm font-semibold">
              {killEnabled === null ? 'Unknown' : killEnabled ? 'ACTIVE' : 'DISABLED'}
            </div>
          </div>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Risk Parameters</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm mb-2">Max Position Size (%)</label>
            <input
              type="number"
              value={settings.max_position_size ?? 5}
              onChange={(e) => setSettings({ ...settings, max_position_size: parseFloat(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Max Daily Loss (%)</label>
            <input
              type="number"
              value={settings.max_daily_loss ?? 2}
              onChange={(e) => setSettings({ ...settings, max_daily_loss: parseFloat(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Max Correlation</label>
            <input
              type="number"
              step="0.01"
              value={settings.max_correlation ?? 0.7}
              onChange={(e) => setSettings({ ...settings, max_correlation: parseFloat(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Ollama LLM Configuration</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Model</label>
            <select
              value={settings.ollama_model || 'qwen2.5:3b'}
              onChange={(e) => setSettings({ ...settings, ollama_model: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="qwen2.5:3b">qwen2.5:3b (Fast)</option>
              <option value="deepseek-r1:7b">deepseek-r1:7b (Reasoning)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-2">Server URL</label>
            <input
              type="text"
              value={settings.ollama_url || 'http://localhost:11434'}
              onChange={(e) => setSettings({ ...settings, ollama_url: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
        </div>
        <button onClick={handleTestConnection} className="mt-4 px-4 py-2 bg-green-600 rounded hover:bg-green-700 text-sm">
          Test Connection
        </button>
        <div className="mt-2 text-xs text-gray-400">
          Note: the Render-hosted dashboard cannot reach your laptop's `localhost`. This test is useful only when running the
          frontend locally.
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Telegram Notifications</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Enabled</label>
            <select
              value={String(settings.telegram_enabled ?? true)}
              onChange={(e) => setSettings({ ...settings, telegram_enabled: e.target.value === 'true' })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="true">Enabled</option>
              <option value="false">Disabled</option>
            </select>
          </div>
          <div />

          <div>
            <label className="block text-sm mb-2">Bot Token</label>
            <input
              type="password"
              value={settings.telegram_bot_token || ''}
              onChange={(e) => setSettings({ ...settings, telegram_bot_token: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="***masked***"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Chat ID</label>
            <input
              type="text"
              value={settings.telegram_chat_id || ''}
              onChange={(e) => setSettings({ ...settings, telegram_chat_id: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="123456789"
            />
          </div>
        </div>
        <button onClick={handleTelegramTest} className="mt-4 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 text-sm">
          Test Telegram
        </button>
        <div className="mt-2 text-xs text-gray-400">
          Buy alerts have a 60 second cooldown per symbol (configured by `TELEGRAM_ALERT_COOLDOWN_SECONDS`).
        </div>
      </section>

      <section className="mb-8 bg-gray-900 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Hermes AI Strategy Engine</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm mb-2">Hermes Enabled</label>
            <select
              value={String(settings.hermes_enabled ?? true)}
              onChange={(e) => setSettings({ ...settings, hermes_enabled: e.target.value === 'true' })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            >
              <option value="true">Enabled</option>
              <option value="false">Disabled</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-2">Hermes Command (optional override)</label>
            <input
              type="text"
              value={settings.hermes_cmd || ''}
              onChange={(e) => setSettings({ ...settings, hermes_cmd: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
              placeholder="wsl hermes"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Timeout (seconds)</label>
            <input
              type="number"
              value={settings.hermes_timeout_sec ?? 120}
              onChange={(e) => setSettings({ ...settings, hermes_timeout_sec: parseInt(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm mb-2">Strategy Gen Interval (seconds)</label>
            <input
              type="number"
              value={settings.strategy_gen_interval ?? 300}
              onChange={(e) => setSettings({ ...settings, strategy_gen_interval: parseInt(e.target.value) })}
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2"
            />
          </div>
        </div>
        <div className="mt-4 text-xs text-gray-400">
          Hermes powers AI strategy generation, validation, tuning, and explanation. Requires Hermes Agent installed locally or via SSH.
        </div>
      </section>

      <button
        onClick={handleSave}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded"
      >
        {saved ? 'Saved!' : 'Save Settings'}
      </button>
    </div>
  );
}
