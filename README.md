# 🤖 Claude Collector

**One command to extract all your Claude Code conversations for training datasets.**

## Quick Start

### Install and run with uvx (recommended)

```bash
uvx claude-collector
```

That's it! The tool will:
- ✅ Auto-find your Claude Code data (`~/.claude/projects`)
- ✅ Extract all conversations
- ✅ Sanitize PII (emails, API keys, paths)
- ✅ Count total tokens
- ✅ Save as training-ready JSONL

### Or install globally

```bash
uv tool install claude-collector
claude-collector
```

## What It Does

Scans your Claude Code session files and:

1. **Finds** all conversation data in `~/.claude/projects`
2. **Extracts** user/assistant message pairs
3. **Sanitizes** sensitive information:
   - Emails → `[EMAIL]`
   - API keys → `[API_KEY]`
   - File paths → `/Users/[USER]/...`
   - IP addresses → `[IP]`
   - OAuth tokens → `[REDACTED]`
4. **Counts** actual token usage
5. **Saves** as clean JSONL dataset

## Example Output

```
🤖 Claude Collector v0.1.0
Extract & sanitize Claude Code conversations

✓ Found Claude data: /Users/z/.claude/projects

📂 Processing 1394 files...

╭─────────────────────┬──────────────╮
│ Metric              │ Value        │
├─────────────────────┼──────────────┤
│ Files scanned       │ 1,394        │
│ Files with data     │ 1,273        │
│ Total messages      │ 46,029       │
│ Training examples   │ 3,653        │
│ Total tokens        │ 4.04B        │
╰─────────────────────┴──────────────╯

✅ Dataset saved!
   File: claude_dataset_20251113.jsonl
   Size: 19.13 MB
   Examples: 3,653

🎉 Ready for training!
```

## Options

```bash
# Dry run (see stats without saving)
uvx claude-collector --dry-run

# Custom output location
uvx claude-collector --output ~/my-dataset.jsonl

# Specify input directory
uvx claude-collector --input ~/.config/claude/projects

# Filter by minimum tokens
uvx claude-collector --min-tokens 1000

# Skip sanitization (NOT recommended for sharing!)
uvx claude-collector --no-sanitize
```

## Use Cases

### 1. Create Training Dataset

```bash
uvx claude-collector --output training-data.jsonl
```

### 2. Audit Your Usage

```bash
uvx claude-collector --dry-run
```

Shows total tokens without saving.

### 3. Collect from Multiple Machines

On each computer:

```bash
# Machine 1
uvx claude-collector --output machine1-data.jsonl

# Machine 2  
uvx claude-collector --output machine2-data.jsonl

# Combine later
cat machine1-data.jsonl machine2-data.jsonl > combined-dataset.jsonl
```

### 4. Add to Existing Dataset

```bash
uvx claude-collector --output new-sessions.jsonl
cat existing-dataset.jsonl new-sessions.jsonl > updated-dataset.jsonl
```

## Output Format

Each line is a JSON object:

```json
{
  "messages": [
    {"role": "user", "content": "How do I..."},
    {"role": "assistant", "content": "You can..."}
  ],
  "metadata": {
    "timestamp": "2025-11-13T...",
    "tokens": {
      "input_tokens": 100,
      "output_tokens": 200,
      "cache_creation_input_tokens": 5000,
      "cache_read_input_tokens": 1000
    }
  }
}
```

Perfect for:
- Fine-tuning LLMs
- Training coding assistants
- Building instruction datasets
- Analysis and research

## Finding Claude Data

### Default Locations

```bash
~/.claude/projects/              # Primary
~/.config/claude/projects/       # Alternative
```

### Check All Users

```bash
ls -la /Users/*/.claude/projects     # macOS
ls -la /home/*/.claude/projects      # Linux
```

### Find Anywhere

```bash
find ~ -name "*.jsonl" -path "*/.claude/*" 2>/dev/null
```

## Privacy & Security

⚠️ **Important**: Claude Code logs contain sensitive data!

**The tool sanitizes:**
- ✅ Email addresses
- ✅ API keys and tokens
- ✅ File paths (username removed)
- ✅ IP addresses
- ✅ OAuth credentials
- ✅ Passwords

**Still check before sharing:**
- Project names (if sensitive)
- Company-specific terminology
- Proprietary code patterns

For maximum privacy, review the output file before uploading anywhere.

## Requirements

- Python 3.8+
- Claude Code installed (for data to exist)

## Installation Methods

### 1. uvx (easiest, no install)
```bash
uvx claude-collector
```

### 2. uv tool (global install)
```bash
uv tool install claude-collector
claude-collector
```

### 3. pip
```bash
pip install claude-collector
claude-collector
```

### 4. From source
```bash
git clone https://github.com/hanzoai/claude-collector
cd claude-collector
uv pip install -e .
claude-collector
```

## Troubleshooting

**"No Claude Code data found"**
- Make sure Claude Code is installed
- Check you've had at least one session
- Try specifying path: `--input ~/.claude/projects`

**"Only found a few conversations"**
- This is normal if you're new to Claude Code
- Each session creates one file
- More usage = more data

**"Tokens show 0"**
- Some messages don't have usage tracking
- This is normal for system messages
- Real conversations will have token counts

## Advanced: Custom Processing

```python
import json

# Read dataset
with open('claude_dataset.jsonl', 'r') as f:
    for line in f:
        example = json.loads(line)
        
        # Access messages
        user_msg = example['messages'][0]['content']
        assistant_msg = example['messages'][1]['content']
        
        # Access metadata
        tokens = example['metadata']['tokens']
        timestamp = example['metadata']['timestamp']
        
        # Your custom processing here
```

## License

MIT - Free to use for any purpose

## Credits

Built by [Hanzo AI](https://hanzo.ai) for the AI development community.

---

**Found a bug?** Open an issue: https://github.com/hanzoai/claude-collector/issues
**Want to contribute?** PRs welcome!
