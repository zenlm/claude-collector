#!/usr/bin/env python3
"""
Claude Collector - Full Agentic Data Extraction
Preserves ALL tool calls, metadata, and context for agent training
"""

import json
import re
from pathlib import Path
from datetime import datetime
import click
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

def sanitize(text):
    """Minimal sanitization - only critical PII"""
    if not isinstance(text, str):
        return str(text)
    # Only sanitize truly sensitive data
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    text = re.sub(r'sk-[a-zA-Z0-9]{48}', '[API_KEY]', text)
    text = re.sub(r'/Users/([^/\s]+)', r'/Users/[USER]', text)  # Keep structure
    return text

def process_file_full(path):
    """Extract EVERYTHING - full agentic data"""
    entries, tokens = [], 0
    
    try:
        for line in open(path, 'r', errors='ignore'):
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                
                # Keep EVERYTHING except pure metadata
                entry_type = data.get('type', '')
                
                # Skip only pure metadata/snapshots
                if entry_type in ['summary', 'file-history-snapshot', 'queue-operation']:
                    continue
                
                # Sanitize content if present
                if 'message' in data and isinstance(data['message'], dict):
                    if 'content' in data['message']:
                        content = data['message']['content']
                        if isinstance(content, str):
                            data['message']['content'] = sanitize(content)
                        elif isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict) and 'text' in item:
                                    item['text'] = sanitize(item['text'])
                
                # Count tokens
                usage = data.get('message', {}).get('usage', {}) or data.get('usage', {})
                if usage:
                    tokens += (usage.get('input_tokens', 0) +
                              usage.get('output_tokens', 0) +
                              usage.get('cache_creation_input_tokens', 0) +
                              usage.get('cache_read_input_tokens', 0))
                
                # Keep the FULL entry with all metadata
                entries.append(data)
                
            except:
                pass
    except:
        pass
    
    return entries, tokens

@click.command()
@click.option('--input', '-i', type=click.Path(exists=True), 
              help='Input directory (default: ~/.claude/projects)')
@click.option('--output', '-o', type=click.Path(),
              help='Output file (default: claude_full_YYYYMMDD.jsonl)')
@click.option('--dry-run', is_flag=True, help='Show stats without saving')
@click.option('--full', is_flag=True, default=True,
              help='Include ALL data (tool calls, metadata) for agentic training')
def main(input, output, dry_run, full):
    """
    🤖 Claude Collector - Extract Claude Code for Agent Training
    
    Extracts FULL agentic data including:
    - User/assistant conversations
    - Tool calls and responses  
    - Agent invocations
    - All metadata and context
    
    Perfect for training coding agents!
    
    \b
    Usage:
        uvx claude-collector                    # Extract everything
        uvx claude-collector --dry-run          # Just show stats
        uvx claude-collector -o my-data.jsonl   # Custom output
    """
    
    console.print("\n[bold cyan]🤖 Claude Collector v0.1.0[/bold cyan]")
    console.print("[dim]Full Agentic Data Extraction[/dim]\n")
    
    # Find data
    if input:
        dir = Path(input)
    else:
        dir = Path.home() / '.claude' / 'projects'
        if not dir.exists():
            dir = Path.home() / '.config' / 'claude' / 'projects'
    
    if not dir.exists():
        console.print(f"[red]❌ No Claude data found at {dir}[/red]")
        console.print("\nTry: --input /path/to/claude/projects")
        return
    
    console.print(f"[green]✓[/green] Found: {dir}")
    console.print(f"[yellow]⚙️[/yellow]  Mode: FULL (includes tool calls & metadata)\n")
    
    files = list(dir.rglob('*.jsonl'))
    console.print(f"[cyan]📂 Processing {len(files)} files...[/cyan]\n")
    
    all_entries, total_tokens, file_count = [], 0, 0
    entry_types = {}
    
    for f in track(files, description="Extracting"):
        entries, toks = process_file_full(f)
        if entries:
            all_entries.extend(entries)
            total_tokens += toks
            file_count += 1
            
            # Track entry types
            for e in entries:
                t = e.get('type', 'unknown')
                entry_types[t] = entry_types.get(t, 0) + 1
    
    # Results table
    t = Table(title="Extraction Results")
    t.add_column("Metric", style="cyan")
    t.add_column("Value", style="green")
    t.add_row("Files scanned", f"{len(files):,}")
    t.add_row("Files with data", f"{file_count:,}")
    t.add_row("Total entries", f"{len(all_entries):,}")
    t.add_row("Total tokens", f"{total_tokens:,} ({total_tokens/1e9:.2f}B)")
    
    console.print()
    console.print(t)
    
    # Show entry types
    console.print("\n[cyan]Entry Types:[/cyan]")
    for etype, count in sorted(entry_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        console.print(f"  • {etype}: {count:,}")
    console.print()
    
    if dry_run:
        console.print("[yellow]🔍 DRY RUN - No files saved[/yellow]\n")
        return
    
    # Save FULL dataset
    out = Path(output) if output else Path(f"claude_full_{datetime.now().strftime('%Y%m%d_%H%M')}.jsonl")
    out.parent.mkdir(parents=True, exist_ok=True)
    
    with open(out, 'w') as f:
        for entry in all_entries:
            f.write(json.dumps(entry) + '\n')
    
    size = out.stat().st_size / 1024 / 1024
    
    console.print(f"[green]✅ Full dataset saved![/green]")
    console.print(f"   File: [cyan]{out.name}[/cyan]")
    console.print(f"   Size: [cyan]{size:.2f} MB[/cyan]")
    console.print(f"   Entries: [cyan]{len(all_entries):,}[/cyan]")
    console.print(f"   Tokens: [cyan]{total_tokens:,} ({total_tokens/1e9:.2f}B)[/cyan]")
    console.print(f"\n[bold green]🎉 Ready for agentic training![/bold green]\n")

if __name__ == '__main__':
    main()
