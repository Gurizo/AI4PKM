# AI4PKM CLI

**Personal Knowledge Management CLI Framework**

Version: 0.1.0

A powerful command-line interface for automating knowledge management workflows using AI assistance. The CLI provides scheduled prompt execution, interactive report generation, and seamless integration with Claude AI through the Claude Code SDK.

## 🚀 Features

- **📅 Cron Job Scheduling**: Automated execution of knowledge management tasks
- **🤖 AI Integration**: Powered by Claude AI through Claude Code SDK
- **📊 Interactive Report Generation**: Guided report creation with templates
- **🎨 Rich Terminal Interface**: Beautiful console UI with colors and panels
- **📝 Prompt Management**: Support for both named prompts and inline prompts
- **🔍 Template System**: Parameterized templates for content generation
- **📋 Comprehensive Logging**: File and console logging with multiple levels

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Claude Code SDK access

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install as Package

```bash
pip install -e .
```

After installation, the CLI will be available as the `ai4pkm` command.

## 🎯 Usage

The CLI operates in several modes:

### 1. Default Mode (Information Display)

Run the CLI without arguments to see current configuration and usage instructions:

```bash
ai4pkm
```

This will:
- Show current agent configuration
- Display scheduled cron jobs
- List common commands and shortcuts
- Provide quick usage reference

### 2. Continuous Cron Mode

Start the cron job scheduler for automated task execution:

```bash
ai4pkm -c
# or
ai4pkm --cron
```

This will:
- Load and start configured cron jobs
- Run continuously with live logging
- Execute scheduled tasks automatically
- Continue running until stopped with Ctrl+C

### 3. One-time Prompt Execution

Execute a specific prompt immediately:

```bash
# Run a named prompt from _Settings_/Prompts/
ai4pkm -p "Generate Daily Roundup (GDR)"

# Run using shortcut code
ai4pkm -p "GDR"

# Run special report generator
ai4pkm -p "generate_report"

# Run an adhoc prompt
ai4pkm -p "custom_prompt"
```

**Named Prompt Resolution:**
1. Exact match (case insensitive)
2. Shortcut code matching (e.g., "GDR" matches "Generate Daily Roundup (GDR)")
3. Partial name matching
4. Fallback to Adhoc folder

**Per-Prompt Agent Override:**
You can use a specific agent for just one prompt without changing the global configuration:

```bash
# Use Gemini for this prompt only
ai4pkm -a g -p "GDR"

# Use Codex for this prompt only  
ai4pkm -a codex -p "TKC"

# Global agent remains unchanged
ai4pkm --show-config
```

### 4. Cron Job Testing

Test a specific cron job interactively:

```bash
ai4pkm -t
```

This will:
- Display all configured cron jobs
- Allow you to select and test a job
- Show execution time and results
- Useful for debugging scheduled tasks

### 5. AI Agent Management

The CLI supports multiple AI agents. Manage them using these commands:

```bash
# List all available agents and their status
ai4pkm --list-agents

# Show current configuration
ai4pkm --show-config

# Switch to a different agent (full names)
ai4pkm --agent claude_code
ai4pkm --agent gemini_cli
ai4pkm --agent codex_cli

# Or use convenient shortcuts
ai4pkm -a c       # Claude
ai4pkm -a g       # Gemini  
ai4pkm -a o       # Codex

# Or use full names
ai4pkm -a claude  # Claude
ai4pkm -a gemini  # Gemini
ai4pkm -a codex   # Codex
```

**Available Agents:**
- **Claude Code**: Uses Claude Code SDK (default)
- **Gemini CLI**: Uses Google Gemini CLI
- **Codex CLI**: Uses OpenAI Codex CLI

The system automatically falls back to available agents if the selected one is not configured.

## ⚙️ Configuration

### AI Agent Configuration (`_Settings_/ai4pkm_config.json`)

The CLI automatically creates a configuration file to manage AI agent settings:

```json
{
  "agent": "claude_code",
  "claude_code": {
    "permission_mode": "bypassPermissions"
  },
  "gemini_cli": {
    "command": "gemini"
  },
  "codex_cli": {
    "command": "codex"
  }
}
```

**Configuration Options:**
- `agent`: Current active agent (claude_code, gemini_cli, codex_cli)  
- Each agent section contains agent-specific settings
- CLI commands can be customized for different installations
- CLI-based agents (Gemini, Codex) use their respective default models

### Cron Jobs (`cron.json`)

Define scheduled tasks in the root `cron.json` file:

```json
[
  {
    "inline_prompt": "CKU for hourly run",
    "cron": "0 * * * *",
    "description": "Regularly run tasks for keeping knowledge base clean every hour"
  },
  {
    "inline_prompt": "DIR for today", 
    "cron": "0 21 * * *",
    "description": "Daily ingestion and processing of contents into daily roundup at 9 PM"
  },
  {
    "inline_prompt": "WRP for this week",
    "cron": "0 12 * * 0", 
    "description": "Weekly review of knowledge base every Sunday at 12 PM"
  }
]
```

**Cron Expression Format:**
- `* * * * *` = minute hour day month weekday
- Examples:
  - `0 * * * *` = Every hour at minute 0
  - `0 21 * * *` = Every day at 9 PM
  - `0 12 * * 0` = Every Sunday at 12 PM

### Prompts Directory Structure

```
_Settings_/
├── Prompts/
│   ├── Generate Daily Roundup (GDR).md
│   ├── Topic Knowledge Creation (TKC).md
│   ├── Process Life Logs (PLL).md
│   └── Adhoc/
│       └── custom_prompt.md
└── Templates/
    ├── Journal Template.md
    ├── Topic Template.md
    └── Weekly Roundup Template.md
```

### Template Parameters

Templates support parameter substitution using `{parameter_name}` syntax:

```markdown
# {name} - {description}

Generated on: {timestamp}
Time range: {start_time} to {end_time}

{template_content}
```

## 🔧 Architecture

### Core Components

| Component | Purpose |
|-----------|---------|
| `main.py` | CLI entry point and argument parsing |
| `cli.py` | Main application logic and user interface |
| `claude_runner.py` | Claude AI integration and prompt execution |
| `cron_manager.py` | Cron job scheduling and execution |
| `logger.py` | Logging infrastructure with file and console output |
| `utils.py` | Interactive utilities (menu selection, etc.) |

### Prompt Runners

| Runner | Purpose |
|--------|---------|
| `report_generator.py` | Interactive report generation with templates |

### Data Flow

1. **Continuous Mode**: CronManager → ClaudeRunner → Logger
2. **One-time Execution**: CLI → ClaudeRunner → Logger  
3. **Interactive Testing**: CLI → CronManager → ClaudeRunner → Logger


## 🐛 Troubleshooting

### Common Issues

1. **"Claude Code SDK not available"**
   - Install: `pip install claude-code-sdk`
   - Verify API credentials

2. **"No cron.json found"**
   - Create `cron.json` in the project root
   - Use the example format above

3. **"Prompt file not found"**
   - Check `_Settings_/Prompts/` directory
   - Verify file naming (include .md extension in files)

4. **Cron jobs not running**
   - Verify cron expression syntax
   - Check log output for errors
   - Test individual jobs with `-t` flag

5. **Agent not available**
   - Use `--list-agents` to check agent status
   - For Gemini CLI: Install Google AI CLI tools
   - For Codex CLI: Install OpenAI CLI tools
   - System automatically falls back to available agents

6. **Agent switching not working**
   - Check `_Settings_/ai4pkm_config.json` permissions
   - Verify agent type spelling (claude_code, gemini_cli, codex_cli)
   - Use shortcuts: `-a c/claude`, `-a g/gemini`, `-a o/codex`
   - Use `--show-config` to verify current settings
   - Per-prompt agents: `ai4pkm -a g -p "prompt"` doesn't change global config

### Debug Mode

For detailed debugging, check the logs in `_Settings_/Logs/` or run with verbose console output.

## 📝 Examples

### Daily Knowledge Management

```bash
# Set up daily roundup at 9 PM
echo '[{"inline_prompt": "DIR for today", "cron": "0 21 * * *", "description": "Daily roundup"}]' > cron.json

# Check the configuration
ai4pkm

# Start the scheduler
ai4pkm -c

# Test the job manually
ai4pkm -t
```

### Custom Prompt Execution

```bash
# Run topic knowledge creation
ai4pkm -p "TKC"

# Generate a custom report
ai4pkm -p "generate_report"

# Run adhoc analysis
ai4pkm -p "analyze_recent_notes"
```

### Agent Management

```bash
# Check available agents
ai4pkm --list-agents

# Switch to Gemini for better multilingual support
ai4pkm -a g

# Use Codex for coding tasks  
ai4pkm -a o

# Show current agent configuration
ai4pkm --show-config

# Run a prompt with specific agent (shortcuts work too)
ai4pkm -a c -p "GDR"

# Use different agents for different tasks
ai4pkm -a gemini -p "translate_document"    # Gemini for multilingual tasks
ai4pkm -a codex -p "generate_code"          # Codex for coding tasks
ai4pkm -a claude -p "analyze_content"       # Claude for analysis
```

## 🤝 Contributing

This CLI is part of the AI4PKM knowledge management framework. Follow the existing code patterns and ensure all new features include appropriate logging and error handling.

## 📄 License

See the main project license for details.
