#!/usr/bin/env python3
"""
Claude Collector CLI
Extract and sanitize Claude Code conversations
"""

import json
import re
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.progress import track
from rich.table import Table
from rich import print as rprint

console = Console()

def sanitize_text(text):
    """Remove PII from text"""
    if not isinstance(text, str):
        return str(text)
    
    replacements = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),
        (r'sk-[a-zA-Z0-9]{48}', '[API_KEY]'),
        (r'xox[baprs]-[a-zA-Z0-9-]+', '[SLACK_TOKEN]'),
        (r'/Users/[^/\s]+', '/Users/[USER]'),
        (r'/home/[^/\s]+', '/home/[USER]'),
        (r'C:\\Users\\[^\\]+', 'C:\\Users\\[USER]'),
        (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]'),
        (r'oauth[_-]?token[_-]?secret?["\']?\s*[:=]\s*["\']?[a-f0-9:]+', 'oauth_token=[REDACTED]'),
        (r'(password|passwd|pwd)["\']?\s*[:=]\s*["\'][^"\']+["\']', r'\1=[REDACTED]'),
    ]
    
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def extract_text_content(content):
    """Extract text from content (string or array)"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif 'text' in item:
                    texts.append(item['text'])
            elif isinstance(item, str):
                texts.append(item)
        return '\n'.join(filter(None, texts))
    return str(content)

def process_jsonl_file(file_path):
    """Extract conversations from a JSONL file"""
    messages = []
    total_tokens = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip():
                    continue
                
                try:
                    data = json.loads(line)
                    
                    # Only process actual user/assistant messages
                    if data.get('type') not in ['user', 'assistant']:
                        continue
                    
                    msg = data.get('message', {})
                    if not msg:
                        continue
                    
                    # Extract content
                    content = extract_text_content(msg.get('content', ''))
                    if not content or len(content) < 10:
                        continue
                    
                    # Get usage data (in message.usage or top-level)
                    usage = msg.get('usage') or data.get('usage') or {}
                    
                    token_count = (
                        usage.get('input_tokens', 0) +
                        usage.get('output_tokens', 0) +
                        usage.get('cache_creation_input_tokens', 0) +
                        usage.get('cache_read_input_tokens', 0)
                    )
                    
                    total_tokens += token_count
                    
                    messages.append({
                        'role': data['type'],
                        'content': sanitize_text(content),
                        'timestamp': data.get('timestamp'),
                        'tokens': token_count,
                        'usage': usage
                    })
                    
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
                    
    except Exception:
        pass
    
    return messages, total_tokens

def find_claude_directories():
    """Find all Claude Code data directories"""
    locations = []
    home = Path.home()
    
    # Check common locations
    candidates = [
        home / '.claude' / 'projects',
        home / '.config' / 'claude' / 'projects',
    ]
    
    for loc in candidates:
        if loc.exists() and loc.is_dir():
            locations.append(loc)
    
    return locations

@click.command()
@click.option('--input', '-i', 'input_dir', type=click.Path(exists=True), 
              help='Input directory (auto-detects ~/.claude/projects if not specified)')
@click.option('--output', '-o', 'output_file', type=click.Path(),
              help='Output file (default: claude_dataset_YYYYMMDD.jsonl)')
@click.option('--dry-run', is_flag=True, help='Show stats without saving')
@click.option('--no-sanitize', is_flag=True, help='Skip PII sanitization (NOT RECOMMENDED)')
@click.option('--min-tokens', type=int, default=0, help='Minimum tokens per conversation')
def main(input_dir, output_file, dry_run, no_sanitize, min_tokens):
    """
    🤖 Claude Collector - Extract Claude Code conversations
    
    Extracts and sanitizes your Claude Code conversation history
    into a training dataset.
    
    \b
    Quick start:
        uvx claude-collector
        
    \b
    Custom output:
        uvx claude-collector --output my-dataset.jsonl
        
    \b
    Check what you have:
        uvx claude-collector --dry-run
    """
    
    console.print("\n[bold cyan]🤖 Claude Collector v0.1.0[/bold cyan]")
    console.print("[dim]Extract & sanitize Claude Code conversations[/dim]\n")
    
    # Find Claude directories
    if input_dir:
        dirs = [Path(input_dir)]
    else:
        dirs = find_claude_directories()
    
    if not dirs:
        console.print("[red]❌ No Claude Code data found![/red]")
        console.print("\nChecked:")
        console.print("  • ~/.claude/projects")
        console.print("  • ~/.config/claude/projects")
        console.print("\nSpecify manually: --input /path/to/projects")
        return
    
    console.print(f"[green]✓[/green] Found Claude data: {dirs[0]}\n")
    
    # Find all JSONL files
    all_files = []
    for directory in dirs:
        all_files.extend(directory.rglob('*.jsonl'))
    
    console.print(f"[cyan]📂 Processing {len(all_files)} files...[/cyan]\n")
    
    # Process files
    all_messages = []
    grand_total_tokens = 0
    files_with_data = 0
    
    for file_path in track(all_files, description="Extracting"):
        messages, tokens = process_jsonl_file(file_path)
        if messages:
            all_messages.extend(messages)
            grand_total_tokens += tokens
            files_with_data += 1
    
    # Create training examples (user + assistant pairs)
    examples = []
    i = 0
    while i < len(all_messages) - 1:
        if all_messages[i]['role'] == 'user' and all_messages[i+1]['role'] == 'assistant':
            example_tokens = all_messages[i+1]['tokens']
            
            if example_tokens >= min_tokens:
                examples.append({
                    'messages': [
                        {'role': 'user', 'content': all_messages[i]['content']},
                        {'role': 'assistant', 'content': all_messages[i+1]['content']}
                    ],
                    'metadata': {
                        'timestamp': all_messages[i]['timestamp'],
                        'tokens': all_messages[i+1]['usage']
                    }
                })
            i += 2
        else:
            i += 1
    
    # Display results
    table = Table(title="Extraction Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Files scanned", f"{len(all_files):,}")
    table.add_row("Files with data", f"{files_with_data:,}")
    table.add_row("Total messages", f"{len(all_messages):,}")
    table.add_row("Training examples", f"{len(examples):,}")
    table.add_row("Total tokens", f"{grand_total_tokens:,} ({grand_total_tokens/1e9:.2f}B)")
    
    console.print()
    console.print(table)
    console.print()
    
    if dry_run:
        console.print("[yellow]🔍 DRY RUN - No files saved[/yellow]")
        return
    
    # Save dataset
    if not output_file:
        output_file = f"claude_dataset_{datetime.now().strftime('%Y%m%d_%H%M')}.jsonl"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for example in examples:
            f.write(json.dumps(example) + '\n')
    
    size_mb = output_path.stat().st_size / 1024 / 1024
    
    console.print(f"[green]✅ Dataset saved![/green]")
    console.print(f"   File: [cyan]{output_path.name}[/cyan]")
    console.print(f"   Size: [cyan]{size_mb:.2f} MB[/cyan]")
    console.print(f"   Examples: [cyan]{len(examples):,}[/cyan]")
    console.print(f"\n[bold green]🎉 Ready for training![/bold green]\n")

if __name__ == '__main__':
    main()
