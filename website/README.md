# Hermes Website MVP

Local-only preview (no production deployment):

```bash
git clone --branch feat/dm-code-aware-support https://github.com/sonht/hermes-platform.git
cd hermes-platform
NMPRP_SOURCE_PATH=/absolute/path/to/nmprp python3 website/server.py
```

Open http://127.0.0.1:8099. The source path must point to a **trusted read-only checkout** of sonht/nmprp. No Zalo connection or unrestricted agent execution is enabled. Authentication and an approved Hermes Agent gateway are required before exposing publicly.

Run offline tests: `python3 -m unittest discover -s tests -v`.
