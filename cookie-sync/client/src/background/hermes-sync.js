// src/background/hermes-sync.js
// Hermes Cookie Sync configuration and state management

import { captureCookiesForDomains, formatCookiesForHermes } from './cookie-capture.js';

const DEFAULT_CONFIG = {
  enabled: false,
  webhookUrl: '',
  apiKey: '',
  syncDomains: [], // Array of domain strings to sync
  autoSync: false, // Auto-sync on cookie changes
};

export async function getSyncConfig() {
  try {
    const result = await chrome.storage.local.get('hermesSyncConfig');
    return { ...DEFAULT_CONFIG, ...result.hermesSyncConfig };
  } catch (error) {
    console.error('[HermesSync] Failed to load config');
    return DEFAULT_CONFIG;
  }
}

export async function setSyncConfig(config) {
  try {
    await chrome.storage.local.set({ hermesSyncConfig: config });
    return { success: true };
  } catch (error) {
    console.error('[HermesSync] Failed to save config');
    return { success: false, error: error.message };
  }
}

export async function isSyncEnabled() {
  const config = await getSyncConfig();
  return config.enabled && config.webhookUrl && config.apiKey;
}

export async function addSyncDomain(domain) {
  const config = await getSyncConfig();
  if (!config.syncDomains.includes(domain)) {
    config.syncDomains.push(domain);
    await setSyncConfig(config);
  }
  return config.syncDomains;
}

export async function removeSyncDomain(domain) {
  const config = await getSyncConfig();
  config.syncDomains = config.syncDomains.filter(d => d !== domain);
  await setSyncConfig(config);
  return config.syncDomains;
}

export async function sendWebhookSync() {
  const config = await getSyncConfig();
  if (!config.enabled || !config.webhookUrl) {
    return { success: false, error: 'Sync not enabled or webhook URL missing' };
  }

  try {
    const { cookies, domains } = await captureCookiesForDomains();
    if (cookies.length === 0) {
      return { success: false, error: 'No cookies found for configured domains' };
    }

    // Group cookies by domain
    const cookiesByDomain = {};
    for (const cookie of cookies) {
      const domain = cookie.domain;
      if (!cookiesByDomain[domain]) {
        cookiesByDomain[domain] = [];
      }
      cookiesByDomain[domain].push(cookie);
    }

    // Send webhook for each domain
    const results = [];
    for (const [domain, domainCookies] of Object.entries(cookiesByDomain)) {
      const payload = formatCookiesForHermes(domainCookies, domain);
      
      const response = await fetch(config.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${config.apiKey}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        results.push({ domain, success: false, status: response.status });
      } else {
        results.push({ domain, success: true });
      }
    }

    const allSuccess = results.every(r => r.success);
    return { success: allSuccess, results };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export async function testWebhookConnection() {
  const config = await getSyncConfig();
  if (!config.webhookUrl) {
    return { success: false, error: 'Webhook URL not configured' };
  }

  try {
    const testPayload = {
      type: 'connection_test',
      timestamp: new Date().toISOString(),
    };

    const response = await fetch(config.webhookUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.apiKey}`,
      },
      body: JSON.stringify(testPayload),
    });

    return {
      success: response.ok,
      status: response.status,
      statusText: response.statusText,
    };
  } catch (error) {
    return { success: false, error: error.message };
  }
}
