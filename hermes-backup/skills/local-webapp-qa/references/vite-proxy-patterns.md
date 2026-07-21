# Frontend Dev Server Proxy Configurations

Quick reference for configuring API proxy in common frontend dev servers.

## Vite

```ts
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

## Create React App (CRA)

```json
// package.json
{
  "proxy": "http://localhost:8000"
}
```

## Next.js

```js
// next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ]
  },
}
```

## Nuxt.js

```js
// nuxt.config.ts
export default defineNuxtConfig({
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

## Angular

```json
// angular.json (in serve options)
{
  "proxyConfig": "proxy.conf.json"
}
```

```json
// proxy.conf.json
{
  "/api": {
    "target": "http://localhost:8000",
    "secure": false,
    "changeOrigin": true
  }
}
```

## General Pattern

The frontend dev server must forward API requests to the backend. Without this:
- Frontend sends `GET /api/v1/tasks` to `localhost:5173` (itself)
- Dev server returns 404 (no such route)
- App shows loading spinner or error state
- Console shows "Failed to load resource: 404"
