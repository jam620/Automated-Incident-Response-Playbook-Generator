# From Hours to Seconds: Meet the Gemini-Powered Automated IR Playbook Generator  
A Free, Open-Source Tool Every Blue Team Needs in 2026

---

## 📝 Credits & Version Information

**Original Author:** [rod-trent](https://github.com/rod-trent)  
**Original Repository:** https://github.com/rod-trent/JunkDrawer/tree/main/Automated%20Incident%20Response%20Playbook%20Generator

**Updated Version:** Migrated from Grok (xAI) to Google Gemini API  
**Updated by:** Using Cursor AI  
**Changes:**
- ✅ Migrated from Grok API to Google Gemini API
- ✅ Added automatic rate limit handling with exponential backoff
- ✅ Improved error messages and quota information
- ✅ Set `gemini-1.5-flash` as default (best for free tier)
- ✅ Added quota information panel in sidebar

---

I just built something that legitimately made my jaw drop the first time I used it.

You paste a messy incident summary — "LockBit hit 400 endpoints, Cobalt Strike beacons, LSASS dumps, EDR blinded" — and 15 seconds later you get a complete, enterprise-grade, MITRE-mapped incident response playbook with a beautiful interactive flowchart.

No templates. No copy-paste from old runbooks. No 4-hour war-room writing session.

Just Google Gemini doing what it does best, instantly.

Here’s the tool: https://github.com/rod-trent/JunkDrawer/tree/main/Automated%20Incident%20Response%20Playbook%20Generator
(Direct Streamlit one-click deploy coming soon)

### What It Actually Does

You type (or paste) something like this:

> “At 03:14 UTC we detected mass .LOCKY encryption across EMEA. Compromised svc_deploy account used for internal RDP brute-force 48h prior. Cobalt Strike beaconing to known Qakbot C2, LSASS dumps via comsvcs.dll, DCSync observed, Falcon sensor service stopped on 60% of hosts.”

You click “Generate Playbook”.

You instantly receive:

1. Executive Summary  
2. Initial Triage & Detection steps  
3. Immediate + Full Containment actions  
4. Eradication procedures  
5. Recovery & Hardening recommendations  
6. Decision branches (“If C2 persists → deploy decoy hosts”)  
7. Full MITRE ATT&CK mapping table  
8. Interactive Mermaid flowchart of the entire response process  
9. One-click Markdown download (ready for Confluence/Notion/Jira)

### Why This Actually Matters in 2025

- Ransomware dwell time is now measured in hours, not days  
- Most organizations still write playbooks manually (or copy outdated ones)  
- Junior analysts freeze when the playbook says “contain the incident” but doesn’t say how  
- Senior IR leads spend half their life writing the same runbook with tiny variations  

This tool collapses that gap from hours → seconds.

I've personally watched a Tier-2 analyst go from "I don't know where to start" to confidently leading containment in under two minutes — because Gemini handed them a battle-tested, environment-aware playbook on demand.

### Tech Stack (Ridiculously Simple)

- Streamlit (the entire frontend is <300 lines)  
- Google Gemini API (the brain)  
- Mermaid.js (for gorgeous flowcharts)  
- Python dotenv (for your API key)  

That's it.

### Requirements

```txt
streamlit
python-dotenv
google-generativeai
```

(That's literally all you need. No Docker required, but I'll give you one if you want.)

### How to Run It Locally in 60 Seconds

```bash
# 1. Clone it
git clone https://github.com/rotrent/gemini-ir-playbook.git
cd gemini-ir-playbook

# 2. Install deps
pip install streamlit python-dotenv google-generativeai

# 3. Get your Gemini API key
# → https://aistudio.google.com/app/apikey → Create API key

# 4. Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# 5. Launch
streamlit run AIR.py
```

Open http://localhost:8501 and paste any incident.

### Real Example Output (LockBit Scenario)

It even added branches I forgot:
- “If ransom note appears on NAS → isolate air-gapped backups immediately”  
- “If Kerberoasting observed post-containment → force enterprise-wide password reset”

Things senior IR people think of… but only after hours of stress.

### Who This Is For

- Small/medium SOCs that can’t afford Cortex XSOAR or Splunk SOAR  
- Incident commanders who are tired of rewriting the same playbook  
- Red teamers who want realistic blue-team responses for their reports  
- Anyone preparing for CIRT tabletop exercises  
- DFIR consultants who bill by the hour (this thing is dangerous for your margins)

### Current Features

- Full Google Gemini integration (gemini-1.5-flash / gemini-1.5-pro / gemini-2.0-flash-exp)  
- **Automatic rate limit handling** with exponential backoff retry logic
- **Quota information panel** with tips for free tier users
- Interactive, zoomable Mermaid flowcharts  
- Chat-based refinement ("Make this for a 5-person team", "Add Splunk SOAR playbooks", "Focus on cloud")  
- One-click Markdown export  
- Works completely offline once running (except the API call)

### ⚠️ Important: API Quotas & Rate Limits

**Free Tier Recommendations:**
- **`gemini-1.5-flash`** (default) - Best for free tier (15 requests/min, 1M tokens/min)
- `gemini-1.5-pro` - Limited free tier support
- `gemini-2.0-flash-exp` - May require paid plan

The app automatically handles rate limit errors (429) with exponential backoff retries. If you encounter quota errors:
1. Use `gemini-1.5-flash` (recommended and set as default)
2. Check your usage: https://ai.dev/usage?tab=rate-limit
3. Wait for rate limits to reset (usually 1 minute)
4. Consider upgrading: https://ai.google.dev/pricing

### Roadmap (Help Wanted!)

- Export to TheHive/Cortex cases  
- Direct push to Confluence/Jira  
- Playbook versioning & team sharing  
- Integration with MISP for automatic IOC enrichment  
- Docker + Cloud Run one-click deploy buttons  

### Final Thought

We’re entering an era where the bottleneck in incident response is no longer “what should we do?” but “how fast can we decide and execute?”

Tools like this are the difference between a $50k crypto payment and a quiet Tuesday.

Try it. Break it. Improve it.  
The blue team needs this yesterday.

→ https://github.com/rod-trent/JunkDrawer/tree/main/Automated%20Incident%20Response%20Playbook%20Generator

(Star it if it saves your bacon during the next ransom deadline. I’ll know why.)

