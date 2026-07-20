# Hermes Toolkit — GitHub Repository Pattern

## Repository

https://github.com/Amirezamky9/hermes-toolkit

## Structure

```
hermes-toolkit/
├── cookie-sync/          # CacheCat-based browser cookie sync
│   ├── webhook.py        # HTTP server receiving cookies
│   ├── .env.example      # Config template
│   └── README.md
├── telegram-toolkit/     # Telethon-based Telegram automation
│   ├── cli.py            # Unified CLI (search/download/export/monitor/info)
│   ├── music_bot.py      # @whatsmusicbot integration
│   ├── bot_interactor.py # Click buttons in any bot
│   ├── auto_join.py      # Auto-join required channels
│   ├── modules/          # Additional modules from TelegramTools
│   └── config.yaml.example
├── docs/                 # Detailed documentation
├── requirements.txt
├── LICENSE (MIT)
└── README.md
```

## Credits Included

| Project | Used For |
|---------|----------|
| CacheCat (chinmay29hub) | Chrome cookie extension |
| Agent-Reach (Panniantong) | AI agent internet access |
| telegram_media_downloader (Dineshkarthik) | Bulk download |
| TelegramTools (DilshanHarshajith) | Modular scraping |
| Telethon (LonamiWebs) | MTProto client |

## Sensitive Data Excluded

- API keys (use .env.example)
- Session files (.session)
- Cookie files (.json)
- Tokens

## Build Pattern

1. Search GitHub for existing solutions
2. Fork/combine best projects
3. Sanitize (remove credentials)
4. Write documentation
5. Add credits
6. Push to GitHub
