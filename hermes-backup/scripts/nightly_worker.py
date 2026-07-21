#!/usr/bin/env python3
"""
🌙 n8n Nightly Worker — v1.0
================================
اجرا: هر شب ۲ بامداد توسط Cron Job

کارها:
  1. خوندن session-logs امروز
  2. خوندن feedback امروز
  3. session_search برای خطاهای امروز
  4. ترکیب و تولید گزارش روزانه

خروجی: /workspace/n8n-wfb/reports/YYYY-MM-DD-report.yaml
"""

import json
import os
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path

BASE_DIR = Path("/workspace/n8n-wfb")
TODAY = date.today().isoformat()

def read_yaml(path):
    """Simple YAML reader without pyyaml dependency"""
    if not path.exists():
        return None
    with open(path) as f:
        return f.read()

def find_today_files():
    """Find session-log and feedback files for today"""
    results = {}
    
    # Session logs
    sl_path = BASE_DIR / "session-logs" / f"{TODAY}_session-log.yaml"
    if sl_path.exists():
        results["session_log"] = read_yaml(sl_path)
    
    # Feedback
    fb_path = BASE_DIR / "feedback" / f"{TODAY}_feedback.yaml"
    if fb_path.exists():
        results["feedback"] = read_yaml(fb_path)
    
    # Manual fixes
    mf_path = BASE_DIR / "bugs" / "manual-fixes.yaml"
    if mf_path.exists():
        results["manual_fixes"] = read_yaml(mf_path)
    
    return results

def generate_report(data):
    """Generate structured report"""
    report = {
        "report_date": TODAY,
        "generated_at": datetime.now().isoformat(),
        "sources_found": list(data.keys()) if data else [],
        "summary": {
            "errors": 0,
            "fixes": 0,
            "suggestions": 0,
            "model_mistakes": 0,
        },
        "details": data,
        "recommendations": []
    }
    
    # Count items (basic parsing)
    for k, v in data.items():
        if isinstance(v, str):
            report["summary"]["errors"] += v.lower().count("error")
            report["summary"]["errors"] += v.lower().count("bug")
            report["summary"]["fixes"] += v.lower().count("fix")
            report["summary"]["suggestions"] += v.lower().count("suggest")
    
    return report

def save_report(report):
    """Save report as YAML-like text"""
    reports_dir = BASE_DIR / "reports"
    reports_dir.mkdir(exist_ok=True)
    
    path = reports_dir / f"{TODAY}_report.yaml"
    
    with open(path, "w") as f:
        f.write(f"# 🌙 Nightly Report — {TODAY}\n")
        f.write(f"# Generated: {report['generated_at']}\n")
        f.write(f"# ============================================\n\n")
        f.write(f"date: \"{TODAY}\"\n")
        f.write(f"generated_at: \"{report['generated_at']}\"\n\n")
        f.write("# Sources Found\n")
        f.write(f"sources_found: {json.dumps(report['sources_found'])}\n\n")
        
        f.write("# Summary\n")
        for k, v in report["summary"].items():
            f.write(f"{k}: {v}\n")
        
        if report["details"]:
            f.write("\n# Raw Details\n")
            for source, content in report["details"].items():
                f.write(f"\n## {source}\n")
                if content:
                    f.write(content[:2000])  # cap at 2K chars
                    f.write("\n")
        
        if report["recommendations"]:
            f.write("\n# Recommendations\n")
            for r in report["recommendations"]:
                f.write(f"- {r}\n")
    
    return path

def main():
    print(f"🌙 Nightly Worker — {TODAY}")
    print("=" * 40)
    
    # Step 1: find today's data
    data = find_today_files()
    print(f"📂 Sources found: {list(data.keys()) if data else 'none'}")
    
    # Step 2: generate report
    report = generate_report(data)
    
    # Step 3: save
    path = save_report(report)
    print(f"✅ Report saved: {path}")
    
    # Step 4: print summary for cron delivery
    summary = report["summary"]
    print(f"\n📊 Summary: {summary['errors']} errors, {summary['fixes']} fixes, {summary['suggestions']} suggestions")
    
    if not data:
        print("\n💤 No data today. Good night!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
