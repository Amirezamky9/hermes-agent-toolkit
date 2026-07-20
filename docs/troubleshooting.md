# Troubleshooting Guide

## Common Issues

### 1. Cookie Sync

#### Server won't start

**Symptoms:**
```
OSError: [Errno 98] Address already in use
```

**Solution:**
```bash
# Find process using port
lsof -i :9999

# Kill it
kill -9 $(lsof -t -i:9999)

# Restart
python3 cookie-sync/webhook.py
```

#### Extension can't connect

**Symptoms:**
- Extension shows "Connection failed"
- No cookies received

**Solution:**
1. Check server: `curl http://localhost:9999/health`
2. Check token matches
3. Check firewall
4. Try different port

### 2. Telegram Toolkit

#### Login fails

**Symptoms:**
```
RPCError: 400 AUTH_KEY_UNREGISTERED
```

**Solution:**
```bash
# Delete session
rm -f telegram.session

# Re-login
python3 cli.py info @telegram
```

#### FloodWait error

**Symptoms:**
```
FloodWaitError: A wait of 60 seconds is required
```

**Solution:**
Script auto-handles. Just wait.

#### Bot doesn't respond

**Symptoms:**
- BotResponseTimeoutError
- No button clicks work

**Solution:**
1. Check bot is not banned
2. Increase timeout
3. Check subscription requirements

### 3. Research Tools

#### yt-dlp not found

**Symptoms:**
```
bash: yt-dlp: command not found
```

**Solution:**
```bash
# Install
pip install yt-dlp

# Or update
pip install -U yt-dlp
```

#### Twitter search fails

**Symptoms:**
```
Error: Authentication required
```

**Solution:**
```bash
# Set token
export TWITTER_AUTH_TOKEN="your_token"

# Or use agent-reach-update.sh
./research/scripts/agent-reach-update.sh
```

#### Telegram search fails

**Symptoms:**
```
ConnectionError: Cannot connect to Telegram
```

**Solution:**
```bash
# Check Telethon installed
pip install telethon

# Check session exists
ls -la telegram-toolkit/telegram.session

# Re-login if needed
python3 telegram-toolkit/cli.py info @telegram
```

### 4. General

#### Python not found

```bash
# Check Python
python3 --version

# Install if missing
sudo apt install python3
```

#### Module not found

```bash
# Install dependencies
pip install -r requirements.txt
```

#### Permission denied

```bash
# Fix permissions
chmod +x *.py
chmod +x research/scripts/*.sh
chmod 600 .env
```

## Getting Help

1. Check this guide
2. Search GitHub Issues
3. Create new issue with:
   - Error message
   - Steps to reproduce
   - Python version
   - OS

## Credits

Built with:
- [Agent-Reach](https://github.com/Panniantong/Agent-Reach) - AI agent internet access
- [Telethon](https://github.com/LonamiWebs/Telethon) - Telegram MTProto
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video download
- [CacheCat](https://github.com/chinmay29hub/CacheCat) - Chrome cookie extension
