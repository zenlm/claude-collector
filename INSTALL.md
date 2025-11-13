# Quick Install - Claude Collector

## Option 1: Direct from GitHub (Works Now!)

```bash
uvx --from git+https://github.com/hanzoai/claude-collector claude-collector
```

Or shorter with uv:
```bash
uv tool install git+https://github.com/hanzoai/claude-collector
claude-collector
```

## Option 2: Standalone Script (Even Easier!)

Copy-paste this one command:

```bash
curl -sSL https://raw.githubusercontent.com/hanzoai/claude-collector/main/standalone.py | python3 - --output claude-data.jsonl
```

Or download and run:

```bash
curl -O https://raw.githubusercontent.com/hanzoai/claude-collector/main/standalone.py
python3 standalone.py --output my-data.jsonl
```

## Option 3: After PyPI Publish (Soon)

Once published to PyPI:

```bash
uvx claude-collector
```

---

**Right now on van machine, use Option 1:**

```bash
uvx --from git+https://github.com/hanzoai/claude-collector claude-collector --output van-data.jsonl
```

Or Option 2 (curl the standalone script) - coming next!
