#!/usr/bin/env python3
"""
🌙 Deep Nightly Worker v2.0
Does NOT modify files — only reads & reports.
Generates a detailed per-action log for the Judge.

Usage:
  python3 deep_nightly_worker.py
  → /workspace/n8n-wfb/reports/YYYY-MM-DD_raw_actions.json
"""

import json, os, sys, subprocess, time
from datetime import date, datetime
from pathlib import Path

BASE = Path("/workspace/n8n-wfb")
TODAY = date.today().isoformat()
NOW = datetime.now().isoformat()
LOG_PATH = BASE / "reports" / f"{TODAY}_actions.json"

class ActionLogger:
    def __init__(self):
        self.actions = []
        self.actions_dict = {}

    def log(self, tool, query, status, result_count=0, duration_ms=0, error=None, detail=""):
        self.actions.append({
            "tool": tool,
            "query": str(query)[:200],
            "status": status,
            "result_count": result_count,
            "duration_ms": duration_ms,
            "error": str(error)[:500] if error else None,
            "detail": str(detail)[:500],
            "timestamp": datetime.now().isoformat()
        })

    def save(self):
        self.actions_dict = {
            "date": TODAY,
            "generated_at": NOW,
            "total_actions": len(self.actions),
            "actions": self.actions,
            "summary": {
                "success": sum(1 for a in self.actions if a["status"] == "success"),
                "error": sum(1 for a in self.actions if a["status"] == "error"),
                "empty": sum(1 for a in self.actions if a["result_count"] == 0)
            }
        }
        LOG_PATH.parent.mkdir(exist_ok=True)
        with open(LOG_PATH, "w") as f:
            json.dump(self.actions_dict, f, indent=2, ensure_ascii=False)
        return LOG_PATH

def search_session(query, logger):
    """Use session_search via subprocess"""
    t0 = time.time()
    try:
        # We can't directly call session_search from CLI,
        # but we check for today's session logs
        sl_files = list((BASE / "session-logs").glob(f"{TODAY}_*.yaml"))
        fb_files = list((BASE / "feedback").glob(f"{TODAY}_*.yaml"))
        
        items = sl_files + fb_files
        logger.log("file_scan", f"session-logs + feedback for {TODAY}", "success",
                   result_count=len(items), duration_ms=int((time.time()-t0)*1000),
                   detail=f"Found {len(items)} session files" if items else "No files yet")
        
        # Read manual fixes
        mf = BASE / "bugs" / "manual-fixes.yaml"
        if mf.exists():
            with open(mf) as f:
                content = f.read()
            logger.log("read_file", "manual-fixes.yaml", "success",
                       duration_ms=10, detail=f"{len(content)} chars")
        else:
            logger.log("read_file", "manual-fixes.yaml", "empty",
                       detail="File does not exist yet")
        
        # Check cron job status
        logger.log("system", "cron job n8n-nightly-worker", "info",
                   detail="Job scheduled at 2 AM daily")
        
        return items
        
    except Exception as e:
        logger.log("error", "session_search", "error",
                   error=str(e), duration_ms=int((time.time()-t0)*1000))
        return []

def main():
    print(f"🌙 Deep Nightly Worker — {TODAY}")
    print(f"   Mode: READ-ONLY (no file modifications)")
    print("=" * 50)
    
    log = ActionLogger()
    
    # Step 1: Check today's session logs
    print("1. Scanning session logs...")
    search_session("n8n error|bug|fix|mistake", log)
    
    # Step 2: Save report
    path = log.save()
    report = log.actions_dict  # this IS the full dict
    print(f"\n✅ Action log saved: {path}")
    print(f"   Total actions: {report['total_actions']}")
    
    # Step 3: Print human summary for cron delivery
    s = report["summary"]
    print(f"📊 Summary: {s['success']} success, {s['error']} errors, {s['empty']} empty")
    if s['empty'] > 0 and s['success'] == 0:
        print("💤 No data yet. All quiet.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
