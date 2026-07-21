// src/dashboard/views/HermesSyncView.jsx
import React, { useState, useEffect } from 'react';

export default function HermesSyncView() {
  const [config, setConfig] = useState({
    enabled: false,
    webhookUrl: '',
    apiKey: '',
    syncDomains: [],
    autoSync: false,
  });
  const [newDomain, setNewDomain] = useState('');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    loadConfig();
  }, []);

  async function loadConfig() {
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'GET_HERMES_SYNC_CONFIG',
      });
      if (response.success) {
        setConfig(response.config);
      }
    } catch (error) {
      // Silent fail
    }
  }

  async function saveConfig(updates) {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);
    try {
      await chrome.runtime.sendMessage({
        type: 'SET_HERMES_SYNC_CONFIG',
        payload: { config: newConfig },
      });
    } catch (error) {
      // Silent fail
    }
  }

  async function handleSyncNow() {
    setLoading(true);
    setStatus(null);
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'HERMES_SYNC_NOW',
      });
      setStatus(response);
    } catch (error) {
      setStatus({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleTestConnection() {
    setLoading(true);
    setTestResult(null);
    try {
      const response = await chrome.runtime.sendMessage({
        type: 'HERMES_TEST_CONNECTION',
      });
      setTestResult(response);
    } catch (error) {
      setTestResult({ success: false, error: error.message });
    } finally {
      setLoading(false);
    }
  }

  async function handleAddDomain() {
    if (!newDomain.trim()) return;
    const domain = newDomain.trim().toLowerCase();
    if (!config.syncDomains.includes(domain)) {
      await saveConfig({ syncDomains: [...config.syncDomains, domain] });
    }
    setNewDomain('');
  }

  async function handleRemoveDomain(domain) {
    await saveConfig({
      syncDomains: config.syncDomains.filter(d => d !== domain),
    });
  }

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Hermes Sync Configuration
        </h2>
        
        {/* Warning */}
        <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-4 mb-6">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            <strong>Warning:</strong> Cookies are sensitive data. Ensure your webhook URL is secure and uses HTTPS.
          </p>
        </div>

        {/* Enable/Disable Toggle */}
        <div className="flex items-center justify-between mb-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Enable Hermes Sync
          </label>
          <button
            onClick={() => saveConfig({ enabled: !config.enabled })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              config.enabled ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                config.enabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Auto-Sync Toggle */}
        <div className="flex items-center justify-between mb-4">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Auto-Sync on Cookie Changes
          </label>
          <button
            onClick={() => saveConfig({ autoSync: !config.autoSync })}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              config.autoSync ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                config.autoSync ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Webhook URL */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Hermes API URL
          </label>
          <input
            type="url"
            value={config.webhookUrl}
            onChange={(e) => saveConfig({ webhookUrl: e.target.value })}
            placeholder="https://my-hermes-server.com/api/browser-sync"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* API Key */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            API Key (Bearer Token)
          </label>
          <input
            type="password"
            value={config.apiKey}
            onChange={(e) => saveConfig({ apiKey: e.target.value })}
            placeholder="your-api-key"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
          />
        </div>

        {/* Sync Domains */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sync Domains
          </label>
          <div className="flex gap-2 mb-2">
            <input
              type="text"
              value={newDomain}
              onChange={(e) => setNewDomain(e.target.value)}
              placeholder="google.com"
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              onKeyPress={(e) => e.key === 'Enter' && handleAddDomain()}
            />
            <button
              onClick={handleAddDomain}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Add
            </button>
          </div>
          <div className="space-y-2">
            {config.syncDomains.map((domain) => (
              <div
                key={domain}
                className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 rounded-md px-3 py-2"
              >
                <span className="text-sm text-gray-700 dark:text-gray-300">{domain}</span>
                <button
                  onClick={() => handleRemoveDomain(domain)}
                  className="text-red-500 hover:text-red-700 text-sm"
                >
                  Remove
                </button>
              </div>
            ))}
            {config.syncDomains.length === 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                No domains configured. Add domains to sync cookies for.
              </p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={handleTestConnection}
            disabled={loading || !config.webhookUrl}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Testing...' : 'TEST CONNECTION'}
          </button>
          <button
            onClick={handleSyncNow}
            disabled={loading || !config.enabled || !config.webhookUrl}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Syncing...' : 'SYNC NOW'}
          </button>
        </div>

        {/* Status Messages */}
        {status && (
          <div
            className={`mt-4 p-3 rounded-md ${
              status.success
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
            }`}
          >
            <p
              className={`text-sm ${
                status.success
                  ? 'text-green-800 dark:text-green-200'
                  : 'text-red-800 dark:text-red-200'
              }`}
            >
              {status.success ? 'Sync completed successfully' : `Sync failed: ${status.error}`}
            </p>
          </div>
        )}

        {testResult && (
          <div
            className={`mt-4 p-3 rounded-md ${
              testResult.success
                ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
            }`}
          >
            <p
              className={`text-sm ${
                testResult.success
                  ? 'text-green-800 dark:text-green-200'
                  : 'text-red-800 dark:text-red-200'
              }`}
            >
              {testResult.success
                ? `Connection successful (Status: ${testResult.status})`
                : `Connection failed: ${testResult.error}`}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
