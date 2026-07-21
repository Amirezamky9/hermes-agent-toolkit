// src/background/cookie-capture.js
// Capture cookies for configured domains

import { getSyncConfig } from './hermes-sync.js';

export async function captureCookiesForDomains() {
  const config = await getSyncConfig();
  if (!config.syncDomains || config.syncDomains.length === 0) {
    return { cookies: [], domains: [] };
  }

  const allCookies = [];
  const matchedDomains = [];

  for (const domain of config.syncDomains) {
    try {
      const cookies = await chrome.cookies.getAll({ domain });
      if (cookies.length > 0) {
        allCookies.push(...cookies);
        matchedDomains.push(domain);
      }
    } catch (error) {
      // Domain not found or permission error - continue
    }
  }

  return { cookies: allCookies, domains: matchedDomains };
}

export function formatCookiesForHermes(cookies, domain) {
  return {
    domain: domain,
    cookies: cookies.map(cookie => ({
      name: cookie.name,
      value: cookie.value,
      domain: cookie.domain,
      path: cookie.path,
      secure: cookie.secure,
      httpOnly: cookie.httpOnly,
      sameSite: cookie.sameSite,
      expirationDate: cookie.expirationDate,
      session: cookie.session,
      storeId: cookie.storeId,
      hostOnly: cookie.hostOnly,
    })),
    timestamp: new Date().toISOString(),
  };
}
