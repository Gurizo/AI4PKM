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

The CLI operates in three main modes:

### 1. Interactive Mode (Default)

Run the CLI without arguments to start continuous mode with cron job scheduling:

```bash
ai4pkm
```

This will:
- Load and display configured cron jobs
- Start the cron scheduler 
- Show live logs
- Continue running until stopped with Ctrl+C

### 2. One-time Prompt Execution

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

### 3. Cron Job Testing

Test a specific cron job interactively:

```bash
ai4pkm -t
```

This will:
- Display all configured cron jobs
- Allow you to select and test a job
- Show execution time and results
- Useful for debugging scheduled tasks

## ⚙️ Configuration

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

### Debug Mode

For detailed debugging, check the logs in `_Settings_/Logs/` or run with verbose console output.

## 📝 Examples

### Daily Knowledge Management

```bash
# Set up daily roundup at 9 PM
echo '[{"inline_prompt": "DIR for today", "cron": "0 21 * * *", "description": "Daily roundup"}]' > cron.json

# Start the scheduler
ai4pkm

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

## 🤝 Contributing

This CLI is part of the AI4PKM knowledge management framework. Follow the existing code patterns and ensure all new features include appropriate logging and error handling.

## 📄 License

See the main project license for details.
