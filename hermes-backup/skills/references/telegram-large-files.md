# Telegram Large File Transfer — Complete Guide

## Size Limits by Method

| Method | Upload | Download | Notes |
|--------|--------|----------|-------|
| Bot API (hosted api.telegram.org) | 50 MB | **20 MB** | Default; bots via BotFather |
| Bot API Local Server (`--local` mode) | **2000 MB** | **Unlimited** | Self-hosted; files served from local path |
| MTProto (regular account) | 2 GB | 2 GB | Telethon, Pyrogram, MadelineProto |
| MTProto (premium account) | 4 GB | 4 GB | Same libraries, premium tier |

**Pitfall — Bot API download limit is 20 MB, not 50 MB.** Many devs know the 50 MB upload limit but forget `getFile` only works for files ≤20 MB on hosted server. Local server removes both limits.

## Decision Matrix

| File Size | Bot Needed? | Best Approach |
|-----------|-------------|---------------|
| ≤20 MB | Yes | Standard Bot API (hosted) — zero config |
| 20–50 MB | Yes | Standard Bot API for upload; Telethon/Pyrogram for download |
| 50 MB–2 GB | Yes | Hybrid: Bot API for UX + MTProto (Telethon) for transfer |
| 50 MB–2 GB | No | Telethon/Pyrogram directly via MTProto |
| >2 GB (regular) | Either | Telethon split+assemble (chunk ≤1.9 GB each) |
| >2 GB (premium) | Either | Telethon direct up to 4 GB; no split needed |

## Approach 1: Telegram Bot API Local Server (Self-Hosted)

**Best for:** Keeping Bot API code but removing size limits. No code changes beyond `BASE_URL`.

**Official source:** https://github.com/tdlib/telegram-bot-api (⭐ 4,363)
**Docker image:** https://github.com/aiogram/telegram-bot-api (⭐ 297)

### Docker quickstart

```yaml
services:
  telegram-bot-api:
    image: aiogram/telegram-bot-api:latest
    environment:
      TELEGRAM_API_ID: "<api_id>"       # from my.telegram.org
      TELEGRAM_API_HASH: "<api_hash>"
      TELEGRAM_LOCAL: "1"               # enables --local mode
    volumes:
      - telegram-bot-api-data:/var/lib/telegram-bot-api
    ports:
      - "8081:8081"
```

### Local mode features (vs hosted)

- Upload files up to **2000 MB** (vs 50 MB hosted)
- Download files **without size limit** (vs 20 MB hosted)
- Upload via **local file path** or `file:///` URI (no HTTP stream needed)
- `getFile` returns **absolute local path** — no second download step
- Any HTTP URL for webhooks (no TLS termination required by Telegram)
- `max_webhook_connections` up to 100,000

### Migration

```bash
# 1. Deregister from hosted server
curl "https://api.telegram.org/bot<TOKEN>/logOut"

# 2. Point bot to local server
BASE_URL = "http://your-server:8081"  # instead of https://api.telegram.org
```

### Pitfall — `--local` mode must be explicit

Without `TELEGRAM_LOCAL=1` or `--local` flag, the server runs in standard mode with the same 50/20 MB limits as hosted. Always set this flag.

## Approach 2: MTProto via Telethon/Pyrogram

**Best for:** Files 20 MB–4 GB, no Bot API constraints needed.

**Libraries by stars:**
- **Pyrogram** (⭐ 4,618) — https://github.com/pyrogram/pyrogram — Python, elegant async API
- **Telethon** (⭐ 10k+) — https://github.com/LonamiWebs/Telethon — Python, mature, installed on this system
- **MadelineProto** (⭐ 3,465) — https://github.com/danog/MadelineProto — PHP, full MTProto
- **TDLib** (⭐ 8,953) — https://github.com/tdlib/td — C++ official cross-platform library
- **WTelegramClient** (⭐ 1,307) — https://github.com/wiz0u/WTelegramClient — C#/.NET

**Key download repos (up to 2 GB per file):**
- **tangyoha/telegram_media_downloader** (⭐ 5,388) — https://github.com/tangyoha/telegram_media_downloader — web UI, cross-platform, private group support
- **Dineshkarthik/telegram_media_downloader** (⭐ 2,675) — https://github.com/Dineshkarthik/telegram_media_downloader — original, Pyrogram-based
- **Gentlesprite/Telegram_Restricted_Media_Downloader** (⭐ 351) — https://github.com/Gentlesprite/Telegram_Restricted_Media_Downloader — Pyrogram, resumable, restricted content

### Telethon upload with progress

```python
from telethon import TelegramClient
import os

client = TelegramClient('session_name', API_ID, API_HASH)

async def upload_large_file(file_path, entity):
    """Upload up to 2GB via MTProto. 4GB for premium."""
    file_size = os.path.getsize(file_path)
    print(f"Uploading {file_size / (1024**3):.2f} GB...")

    await client.send_file(
        entity,
        file_path,
        progress_callback=lambda sent, total: print(
            f"Progress: {sent*100/total:.1f}%"
        ),
        part_size_kb=512,
    )

async def download_large_file(message, output_dir='.'):
    """Download file from any message."""
    file = await message.download_media(file=output_dir)
    print(f"Downloaded to: {file}")
```

### Pyrogram upload example

```python
from pyrogram import Client

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

with app:
    app.send_document(
        "chat_id",
        "big_file.zip",
        progress=lambda current, total: print(f"{current*100/total:.1f}%")
    )
```

## Approach 3: Split/Reassemble (Files >2 GB)

For files exceeding the 2 GB MTProto limit (regular accounts), split before upload.

Our toolkit already has this: `tg_file_transfer.py split/assemble`.
Location: `~/.agent-reach/tools/telegram-toolkit/tg_file_transfer.py`

### Manual split/reassemble pattern

```python
import os, json, hashlib

CHUNK_SIZE = int(1.9 * 1024 * 1024 * 1024)  # 1.9 GB safe limit

def split_file(filepath):
    chunks = []
    part = 0
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            part += 1
            chunk_path = f"{filepath}.part{part:04d}"
            with open(chunk_path, 'wb') as chunk:
                chunk.write(data)
            chunks.append({
                'part': part, 'path': chunk_path,
                'size': len(data),
                'md5': hashlib.md5(data).hexdigest()
            })
    meta = filepath + ".tg_chunk_meta.json"
    json.dump({'original': filepath, 'total': len(chunks),
               'chunks': chunks}, open(meta, 'w'), indent=2)
    return meta

def assemble_file(meta_path):
    meta = json.load(open(meta_path))
    with open(meta['original'], 'wb') as out:
        for chunk in meta['chunks']:
            with open(chunk['path'], 'rb') as f:
                out.write(f.read())
            out.seek(-chunk['size'], 1)
            data = out.read(chunk['size'])
            assert hashlib.md5(data).hexdigest() == chunk['md5']
    return meta['original']
```

### Pitfall — chunk size must be <2 GB

MTProto enforces 2 GB per `send_file`. Use 1.9 GB chunks to leave margin for metadata overhead.

### Pitfall — MD5 verification

Always include checksums in chunk metadata. Network corruption during multi-part upload is non-negligible for multi-GB transfers.

## Approach 4: Hybrid Bot API + MTProto

**Strategy:** Bot API for user interaction (buttons, commands, webhooks), Telethon/Pyrogram for large file operations.

**Repo:** https://github.com/Sankar8098/Advanced-File-Store-Bot (⭐ 1) — uses both Bot API token and API_ID/API_HASH.

**Pattern:**
1. User interacts with Bot API bot (commands, inline buttons)
2. Bot receives file request, delegates to MTProto worker
3. Worker uploads file via Telethon/Pyrogram
4. Worker sends file_id back to Bot API bot for delivery

## Approach 5: Encrypted Chunked Upload (Client-Side)

**Repo:** https://github.com/hinsley/tglfs (⭐ 4) — Telegram Large File Storage

Client-side app (GramJS + WebCrypto): splits, gzip-compresses, AES-256-CTR encrypts, uploads to Telegram channels. No server needed.

## Approach 6: WTelegramBot (.NET)

**Repo:** https://github.com/wiz0u/WTelegramBot (⭐ 94)

C# library that rewrites Bot API on top of MTProto. Drop-in replacement for Telegram.Bot with large file support.

## Other Notable Projects

| Repo | Stars | Description |
|------|-------|-------------|
| [ilteoood/tele_uploader](https://github.com/ilteoood/tele_uploader) | 23 | PHP bot, MadelineProto + Dropbox fallback |
| [alefmanvladimir/BigFiles](https://github.com/alefmanvladimir/BigFiles) | 14 | TON Drive: bypass 2GB using TON blockchain |
| [mohamad-liyaghi/telegram-to-rubika-uploader](https://github.com/mohamad-liyaghi/telegram-to-rubika-uploader) | 14 | Go, Telegram→Rubika for 2GB files |
| [madebyparth/medianest](https://github.com/madebyparth/medianest) | 4 | Flask + MongoDB, chunked uploads |
| [1MrC1/telegram-storage](https://github.com/1MrC1/telegram-storage) | 1 | React + Fastify + GramJS |
| [myrosama/telegram-cloud-backup](https://github.com/myrosama/telegram-cloud-backup) | 4 | Telegram as cloud backup |
| [HirbodBehnam/TelegramFileUploader](https://github.com/HirbodBehnam/TelegramFileUploader) | 2 | Large file upload with metadata |
| [chuhlomin/telegram-large-files-upload](https://github.com/chuhlomin/telegram-large-files-upload) | 1 | Simple Telethon upload with progress |

## Quick Reference: Setup Commands

```bash
# Install Pyrogram (alternative MTProto library)
pip install pyrogram tgcrypto

# Deploy Bot API local server (Docker)
docker run -d -p 8081:8081 --name=telegram-bot-api \
  -v telegram-bot-api-data:/var/lib/telegram-bot-api \
  -e TELEGRAM_API_ID=<id> -e TELEGRAM_API_HASH=<hash> \
  -e TELEGRAM_LOCAL=1 \
  aiogram/telegram-bot-api:latest

# Verify local server
curl http://localhost:8081/getMe
```
