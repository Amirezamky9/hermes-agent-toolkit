#!/usr/bin/env python3
"""
tg_file_transfer.py — انتقال فایل‌های حجیم از طریق Telegram
پشتیبانی از: دانلود، آپلود، split، assemble، resume

استفاده:
  python tg_file_transfer.py download <message_url> --output /path/
  python tg_file_transfer.py upload <file_path> --to @channel
  python tg_file_transfer.py split <file_path> --chunk-size 1.5G
  python tg_file_transfer.py assemble <chunks_dir>
  python tg_file_transfer.py info <file_path>
"""

import asyncio
import argparse
import os
import sys
import math
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime

TOOLKIT_DIR = Path(__file__).parent
SESSION_FILE = TOOLKIT_DIR / "telegram.session"
CHUNK_MARKER = ".tg_chunk_meta.json"

# ---------------------------------------------------------------------------
# Config loading (same pattern as cli.py)
# ---------------------------------------------------------------------------

def load_env():
    # 1. Try env file first
    env_file = Path.home() / ".agent-reach/cookies/telegram.env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key] = val

    api_id = int(os.environ.get("TG_API_ID", "0"))
    api_hash = os.environ.get("TG_API_HASH", "")

    # 2. Fallback: read from config.yaml in toolkit directory
    if not api_id or not api_hash:
        config_file = TOOLKIT_DIR / "config.yaml"
        if config_file.exists():
            import yaml
            cfg = yaml.safe_load(open(config_file))
            api_id = int(cfg.get("api_id", 0))
            api_hash = cfg.get("api_hash", "")

    return {"api_id": api_id, "api_hash": api_hash}


def parse_size(size_str: str) -> int:
    """Parse human size: 1.5G, 500M, 100K, 1000"""
    size_str = size_str.strip().upper()
    multipliers = {"K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}
    if size_str and size_str[-1] in multipliers:
        return int(float(size_str[:-1]) * multipliers[size_str[-1]])
    return int(size_str)


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def parse_message_url(url: str):
    """
    Parse t.me message URL → (chat, msg_id)
    Supports:
      - https://t.me/channel/123
      - https://t.me/c/1234567890/123  (private)
      - @channel/123
      - channel/123
    """
    import re
    url = url.strip()

    # @channel/123 or channel/123
    m = re.match(r'^(@?\w+)/(\d+)$', url)
    if m:
        return m.group(1), int(m.group(2))

    # https://t.me/channel/123
    m = re.match(r'https?://t\.me/(?:c/)?(\w+)/(\d+)', url)
    if m:
        chat = m.group(1)
        # private chats need numeric ID
        if chat.isdigit():
            return int(chat), int(m.group(2))
        return f"@{chat}", int(m.group(2))

    raise ValueError(f"Cannot parse message URL: {url}")


# ---------------------------------------------------------------------------
# Progress bar (no external deps)
# ---------------------------------------------------------------------------

class ProgressTracker:
    def __init__(self, total: int, label: str = ""):
        self.total = total
        self.label = label
        self.start_time = time.time()
        self.last_print = 0
        self.downloaded = 0

    def update(self, chunk: int):
        self.downloaded += chunk
        now = time.time()
        if now - self.last_print < 0.3 and self.downloaded < self.total:
            return
        self.last_print = now

        elapsed = now - self.start_time
        speed = self.downloaded / elapsed if elapsed > 0 else 0
        pct = (self.downloaded / self.total * 100) if self.total > 0 else 0
        bar_len = 30
        filled = int(bar_len * self.downloaded / self.total) if self.total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)

        eta = ((self.total - self.downloaded) / speed) if speed > 0 else 0
        eta_str = f"{int(eta//60)}m{int(eta%60)}s" if eta > 60 else f"{int(eta)}s"

        sys.stdout.write(
            f"\r  {self.label} |{bar}| {pct:.1f}% "
            f"| {human_size(self.downloaded)}/{human_size(self.total)} "
            f"| {human_size(int(speed))}/s | ETA {eta_str}  "
        )
        sys.stdout.flush()

    def finish(self):
        elapsed = time.time() - self.start_time
        speed = self.downloaded / elapsed if elapsed > 0 else 0
        sys.stdout.write(
            f"\r  ✅ {human_size(self.downloaded)} in {elapsed:.1f}s "
            f"({human_size(int(speed))}/s)          \n"
        )
        sys.stdout.flush()


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

async def cmd_download(args):
    """دانلود فایل از یک پیام تلگرام"""
    from telethon import TelegramClient

    env = load_env()
    client = TelegramClient(str(SESSION_FILE), env["api_id"], env["api_hash"])
    await client.start()

    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}\n")

    chat, msg_id = parse_message_url(args.message_url)
    print(f"📥 Fetching message {msg_id} from {chat}...")

    msg = await client.get_messages(chat, ids=msg_id)
    if not msg:
        print("❌ Message not found")
        await client.disconnect()
        return

    if not msg.file:
        print("❌ Message has no file/media")
        print(f"   Text: {(msg.text or '')[:200]}")
        await client.disconnect()
        return

    filename = msg.file.name or f"tg_file_{msg_id}"
    filesize = msg.file.size
    print(f"   File: {filename}")
    print(f"   Size: {human_size(filesize)}")
    print(f"   Type: {type(msg.media).__name__}")

    # Output path
    if args.output:
        out_path = Path(args.output)
        if out_path.is_dir():
            out_path = out_path / filename
    else:
        out_path = Path(filename)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Resume support: check partial download
    temp_path = str(out_path) + ".part"
    resume_from = 0
    if os.path.exists(temp_path) and args.resume:
        resume_from = os.path.getsize(temp_path)
        print(f"\n⏩ Resuming from {human_size(resume_from)}...")
    elif os.path.exists(temp_path) and not args.resume:
        os.remove(temp_path)

    # Download with progress
    progress = ProgressTracker(filesize, "Downloading")
    start_time = time.time()

    async def progress_callback(received, total):
        progress.update(received - (resume_from if resume_from else 0))

    try:
        if resume_from and args.resume:
            # Telethon doesn't natively support resume offset for files,
            # so we download to temp and append
            await client.download_media(
                msg,
                file=temp_path,
                progress_callback=progress_callback,
            )
        else:
            await client.download_media(
                msg,
                file=str(out_path),
                progress_callback=progress_callback,
            )

        # If resume mode, we already saved to temp_path
        if resume_from and args.resume:
            os.rename(temp_path, str(out_path))

        progress.finish()
        print(f"📁 Saved to: {out_path.resolve()}")

    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        if os.path.exists(temp_path):
            print(f"   Partial file saved: {temp_path}")
            print(f"   Resume with: --resume")
    finally:
        await client.disconnect()


async def cmd_upload(args):
    """آپلود فایل به تلگرام"""
    from telethon import TelegramClient

    file_path = Path(args.file_path).expanduser().resolve()
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    filesize = file_path.stat().st_size
    filename = file_path.name

    env = load_env()
    client = TelegramClient(str(SESSION_FILE), env["api_id"], env["api_hash"])
    await client.start()

    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name}\n")

    # Check file size vs Telegram limits
    # Telethon supports up to 2GB (regular) / 4GB (premium)
    # For larger files, suggest split
    MAX_SINGLE = 2 * 1024**3  # 2GB conservative

    if filesize > MAX_SINGLE and not args.force:
        print(f"⚠️  File is {human_size(filesize)} — exceeds 2GB single upload limit")
        print(f"   Use --force to attempt anyway (may work for premium)")
        print(f"   Or split first: python tg_file_transfer.py split {file_path}")
        await client.disconnect()
        return

    # Resolve target
    to_target = args.to
    caption = args.caption or f"📤 {filename}"

    print(f"📤 Uploading: {filename}")
    print(f"   Size: {human_size(filesize)}")
    print(f"   To: {to_target}")
    if args.caption:
        print(f"   Caption: {args.caption}")
    print()

    progress = ProgressTracker(filesize, "Uploading")

    async def progress_callback(sent, total):
        progress.update(sent)

    try:
        await client.send_file(
            to_target,
            file=str(file_path),
            caption=caption,
            progress_callback=progress_callback,
            force_document=True,  # send as document, not auto-detected
        )
        progress.finish()
        print(f"✅ Sent to {to_target}")

    except Exception as e:
        print(f"\n❌ Upload failed: {e}")
    finally:
        await client.disconnect()


async def cmd_split(args):
    """split فایل بزرگ به قطعات"""
    file_path = Path(args.file_path).expanduser().resolve()
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    filesize = file_path.stat().st_size
    chunk_size = parse_size(args.chunk_size)

    if chunk_size >= filesize:
        print(f"❌ Chunk size ({args.chunk_size}) >= file size ({human_size(filesize)})")
        return

    num_chunks = math.ceil(filesize / chunk_size)
    out_dir = Path(args.output or f"{file_path}.chunks")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"✂️  Splitting: {file_path.name}")
    print(f"   Size: {human_size(filesize)}")
    print(f"   Chunk: {args.chunk_size} ({human_size(chunk_size)})")
    print(f"   Parts: {num_chunks}")
    print(f"   Output: {out_dir}\n")

    # Write metadata
    meta = {
        "original_file": file_path.name,
        "original_size": filesize,
        "chunk_size": chunk_size,
        "num_chunks": num_chunks,
        "chunks": [],
        "created": datetime.now().isoformat(),
        "md5": None,
    }

    # Calculate MD5 of original file
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            md5.update(data)
    meta["md5"] = md5.hexdigest()

    progress = ProgressTracker(filesize, "Splitting")
    written = 0

    with open(file_path, "rb") as src:
        for i in range(num_chunks):
            chunk_name = f"{file_path.name}.part{i+1:04d}"
            chunk_path = out_dir / chunk_name
            remaining = min(chunk_size, filesize - written)

            chunk_md5 = hashlib.md5()
            with open(chunk_path, "wb") as dst:
                left = remaining
                while left > 0:
                    read_size = min(8192, left)
                    data = src.read(read_size)
                    if not data:
                        break
                    dst.write(data)
                    chunk_md5.update(data)
                    written += len(data)
                    left -= len(data)
                    progress.update(len(data))

            meta["chunks"].append({
                "index": i,
                "filename": chunk_name,
                "size": remaining,
                "md5": chunk_md5.hexdigest(),
            })
            print(f"  ✅ Part {i+1}/{num_chunks}: {chunk_name} ({human_size(remaining)})")

    # Save metadata
    meta_path = out_dir / CHUNK_MARKER
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    progress.finish()
    print(f"\n📋 Metadata saved: {meta_path}")
    print(f"✅ Split complete: {num_chunks} parts in {out_dir}")

    # Suggest upload command
    print(f"\n💡 To send all parts:")
    print(f"   for f in {out_dir}/*.part*; do")
    print(f"     python tg_file_transfer.py upload \"$f\" --to {args.to or '@channel'}")
    print(f"   done")


async def cmd_assemble(args):
    """assemble قطعات split شده به فایل اصلی"""
    chunks_dir = Path(args.chunks_dir).expanduser().resolve()

    if not chunks_dir.is_dir():
        print(f"❌ Not a directory: {chunks_dir}")
        return

    # Find metadata
    meta_path = chunks_dir / CHUNK_MARKER
    if not meta_path.exists():
        print(f"❌ Metadata not found: {CHUNK_MARKER}")
        print(f"   Looking for .part files instead...")

        # Fallback: find all .part files and sort them
        part_files = sorted(chunks_dir.glob("*.part*"))
        if not part_files:
            print(f"❌ No .part files found in {chunks_dir}")
            return

        meta = None
        total_size = sum(f.stat().st_size for f in part_files)
        num_chunks = len(part_files)
        original_name = part_files[0].name.rsplit(".part", 1)[0]
    else:
        with open(meta_path) as f:
            meta = json.load(f)

        original_name = meta["original_file"]
        num_chunks = meta["num_chunks"]
        total_size = meta["original_size"]

        # Verify all parts exist
        part_files = []
        for chunk in meta["chunks"]:
            cp = chunks_dir / chunk["filename"]
            if not cp.exists():
                print(f"❌ Missing part: {chunk['filename']}")
                return
            part_files.append(cp)

    out_path = Path(args.output or chunks_dir.parent / original_name)

    print(f"🔧 Assembling: {original_name}")
    print(f"   Parts: {num_chunks}")
    print(f"   Size: {human_size(total_size)}")
    print(f"   Output: {out_path}\n")

    progress = ProgressTracker(total_size, "Assembling")
    assembled_md5 = hashlib.md5()

    with open(out_path, "wb") as dst:
        for part_file in part_files:
            with open(part_file, "rb") as src:
                while True:
                    data = src.read(8192)
                    if not data:
                        break
                    dst.write(data)
                    assembled_md5.update(data)
                    progress.update(len(data))

    progress.finish()

    # Verify MD5 if metadata available
    if meta and meta.get("md5"):
        if assembled_md5.hexdigest() == meta["md5"]:
            print(f"✅ MD5 verified: {assembled_md5.hexdigest()}")
        else:
            print(f"⚠️  MD5 mismatch!")
            print(f"   Expected: {meta['md5']}")
            print(f"   Got:      {assembled_md5.hexdigest()}")

    actual_size = out_path.stat().st_size
    print(f"📁 Assembled: {out_path.resolve()} ({human_size(actual_size)})")

    if actual_size != total_size:
        print(f"⚠️  Size mismatch: expected {human_size(total_size)}, got {human_size(actual_size)}")


async def cmd_info(args):
    """نمایش اطلاعات فایل"""
    file_path = Path(args.file_path).expanduser().resolve()

    if file_path.is_dir():
        # Directory info
        total = 0
        count = 0
        for f in file_path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
                count += 1
        print(f"📁 Directory: {file_path}")
        print(f"   Files: {count}")
        print(f"   Total: {human_size(total)}")
        return

    if not file_path.exists():
        print(f"❌ Not found: {file_path}")
        return

    stat = file_path.stat()
    size = stat.st_size

    print(f"📄 File: {file_path.name}")
    print(f"   Size: {human_size(size)} ({size:,} bytes)")
    print(f"   Modified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}")

    # Check if it fits in Telegram
    if size <= 50 * 1024 * 1024:
        print(f"   Telegram Bot API: ✅ (≤50MB)")
    elif size <= 2 * 1024**3:
        print(f"   Telegram Bot API: ❌ (>50MB)")
        print(f"   Telegram MTProto: ✅ (≤2GB)")
    elif size <= 4 * 1024**3:
        print(f"   Telegram MTProto: ✅ (≤4GB, premium)")
    else:
        print(f"   Telegram: ❌ (>4GB, needs split)")

    # MD5
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(8192)
            if not data:
                break
            md5.update(data)
    print(f"   MD5: {md5.hexdigest()}")

    # Check if this is a chunk
    if file_path.suffix.startswith(".part"):
        meta_path = file_path.parent / CHUNK_MARKER
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
            print(f"\n   This is part of: {meta['original_file']}")
            print(f"   Original size: {human_size(meta['original_size'])}")
            print(f"   Total parts: {meta['num_chunks']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="TG File Transfer — انتقال فایل‌های حجیم از طریق Telegram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Commands")

    # download
    p_dl = sub.add_parser("download", help="Download file from a message")
    p_dl.add_argument("message_url", help="Message URL: @channel/123 or https://t.me/channel/123")
    p_dl.add_argument("--output", "-o", help="Output path (file or directory)")
    p_dl.add_argument("--resume", "-r", action="store_true", help="Resume partial download")

    # upload
    p_up = sub.add_parser("upload", help="Upload file to Telegram")
    p_up.add_argument("file_path", help="File to upload")
    p_up.add_argument("--to", "-t", required=True, help="Destination: @channel, @user, or chat_id")
    p_up.add_argument("--caption", "-c", help="Message caption")
    p_up.add_argument("--force", "-f", action="store_true", help="Force upload even if >2GB")

    # split
    p_sp = sub.add_parser("split", help="Split large file into chunks")
    p_sp.add_argument("file_path", help="File to split")
    p_sp.add_argument("--chunk-size", "-s", default="1.5G", help="Chunk size (default: 1.5G)")
    p_sp.add_argument("--output", "-o", help="Output directory")
    p_sp.add_argument("--to", "-t", help="Target for upload suggestion")

    # assemble
    p_asm = sub.add_parser("assemble", help="Assemble chunks back into file")
    p_asm.add_argument("chunks_dir", help="Directory containing .part files")
    p_asm.add_argument("--output", "-o", help="Output file path")

    # info
    p_info = sub.add_parser("info", help="Show file info and Telegram compatibility")
    p_info.add_argument("file_path", help="File or directory path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "download": cmd_download,
        "upload": cmd_upload,
        "split": cmd_split,
        "assemble": cmd_assemble,
        "info": cmd_info,
    }

    asyncio.run(commands[args.command](args))


if __name__ == "__main__":
    main()
