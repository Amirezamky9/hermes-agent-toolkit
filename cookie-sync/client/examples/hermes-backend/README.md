# Hermes Backend Example

A FastAPI backend example for receiving cookies from the Hermes Browser Sync Extension.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export HERMES_API_KEY="your-secret-api-key"
export STORAGE_STATE_PATH="storage_state.json"
```

3. Run the server:
```bash
python main.py
```

The server will start on `http://localhost:8000`.

## API Endpoints

- `POST /api/browser-sync` - Receive cookies from browser extension
- `POST /api/test-connection` - Test connection
- `GET /health` - Health check

## Configuration

Update the extension's Hermes Sync settings with:
- API URL: `http://localhost:8000/api/browser-sync`
- API Key: `your-secret-api-key`

## Storage State Format

The backend saves cookies in Playwright's storage_state.json format:

```json
{
  "cookies": [
    {
      "name": "session_id",
      "value": "abc123",
      "domain": ".example.com",
      "path": "/",
      "secure": true,
      "httpOnly": true,
      "sameSite": "Lax",
      "expires": 1735689600,
      "url": "https://example.com/"
    }
  ],
  "origins": []
}
```
