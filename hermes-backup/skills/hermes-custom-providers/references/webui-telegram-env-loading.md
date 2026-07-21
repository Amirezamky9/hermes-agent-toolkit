# WebUI & Telegram Env-Loading for Custom Providers

When adding a custom provider for WebUI or Telegram use, the key question is: will the platform correctly load the `key_env` variable from `~/.hermes/.env`?

## Answer: Yes, automatically

Both the TUI Gateway (WebUI backend) and the Telegram gateway call `load_hermes_dotenv()` at startup:

```python
# tui_gateway/server.py (line 42-43) — WebUI / Desktop app backend:
load_hermes_dotenv(
    hermes_home=_hermes_home,
    project_env=Path(__file__).parent.parent / ".env"
)

# run_agent.py (line 119-127) — CLI + gateway agent runner:
from hermes_cli.env_loader import load_hermes_dotenv
_loaded_env_paths = load_hermes_dotenv(hermes_home=_hermes_home, project_env=_project_env)
```

`load_hermes_dotenv()` reads `~/.hermes/.env` (or `$HERMES_HOME/.env`) with `override=True`, so entries like `api=sk-...` become available via `os.environ["api"]`.

## What this means

No extra config or script is needed for WebUI or Telegram. As long as:

1. The env var is added to `~/.hermes/.env`
2. The `custom_providers` entry has `key_env: <varname>` matching the env var name
3. Both files are saved before the server starts (or the server is restarted)

...the provider will appear in the model picker with live-discovered models on both platforms.

## If it does NOT appear

1. **Restart required**: Config is read at startup. Use `/reset` in session or restart the gateway/server process.
2. **Check `.env` syntax**: No spaces around `=` for simple values. Quoted values like `api="sk-..."` are fine — `load_hermes_dotenv` handles them.
3. **Verify the env var loads**: Run `python3 -c "import os; print(repr(os.getenv('YOUR_VAR')))"` inside the same process context.
4. **Test the raw endpoint**: `curl -s -H "Authorization: Bearer $YOUR_KEY" https://endpoint/v1/models` — if this fails, the key or URL is wrong regardless of Hermes config.
