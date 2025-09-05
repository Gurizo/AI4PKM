# AI Assistant Guidelines
## Principles
- Your mission is to enhance and organize user’s knowledge
	- Don’t add your internal knowledge unless explicitly asked to do so 
## Prompts & Workflows
- Prompts can be found in `_Settings_/Prompts`
- Workflows (of prompts) in `_Settings_/Workflows`
- Each command can be called using abbreviations
- Check this first for new command (especially if it's abbreviations)

## 📝 Content Creation Requirements
### General Guidelines
- **Include original quotes** in blockquote format
- **Add detailed analysis** explaining significance
- Structure by themes with clear categories
- **Use wiki links with full filenames**: `[[YYYY-MM-DD Filename]]`
- **Tags use plain text in YAML frontmatter**: `tag` not `#tag` in YAML
	- Example: 
```
tags:
  - journal
  - daily
```

### Link Format Standards
- Use Link Format below for page properties:
```
  - "[[Page Title]]"
```
- For files in AI folder, omit "AI/" prefix for brevity
- Example: `[[Roundup/2025-08-03 - AI Assistant]]` not `[[AI/Roundup/2025-08-03 - AI Assistant]]`

### Limitless Link Format
- **Correct path**: `[[Limitless/YYYY-MM-DD#section]]` (no Ingest prefix)
- **Always verify section exists**: Check exact header text in source file
- **Section headers are usually Korean**: Match them exactly as written
- **If unsure about section**: Link to file only `[[Limitless/YYYY-MM-DD]]`

## 📁 File Management
- Create analysis files in `AI/*/` folder unless instructed otherwise
- Naming: `YYYY-MM-DD [Project Name] by [Assistant Name].md`
- Include source attribution for every insight

## 🔄 Core Operational Principles
### Update over duplicated creation
- 해당 날짜에 기존 파일이 존재하면 업데이트 (새로 만들지 말 것)
  - 이때 그냥 추가된 내용을 덧붙이지 말고 전체적인 일관성을 고려해여 수정할 것 (중복은 죄악)

### Language Preferences
- Use Korean as default language (English is fine, say, to quote original note)

### 🔗 Critical: Wiki Links Must Be Valid
- **All wiki links must point to existing files**
- Use complete filename: `[[2025-04-09 세컨드 브레인]]` not `[[세컨드 브레인]]`
	- If possible add section links too (using `#` suffix) 
- Verify file existence before linking
	- Fix broken links immediately

---
# Claude Code Specific Rules

## 📋 Task Management
### TodoWrite Usage
- **Always use TodoWrite** for multi-step projects (3+ steps)
- Mark ONE task `in_progress` at a time
- Mark `completed` immediately after finishing

## Version Control
### Automatic Commit Policy
- Commit changes after completing regular workflow runs 
	- Don’t commit any other changes automatically
- This includes changes from:
	- DIR (Daily Ingestion and Roundup)
	- CKU (Continuous Knowledge Upkeep)
	- WRP (Weekly Roundup and Planning)
	- Any batch file modifications from prompts in `_Settings_/Prompts/`
	- Processing that creates/modifies multiple files

### Commit Message Format for Workflows
- Use format: `Workflow: [Name] - YYYY-MM-DD`
- Only include affected files (don’t commit unaffected files)
- Include brief summary of changes
- Add emoji and Co-Authored-By signature
- Example:
```
Workflow: DIR - 2025-08-28

Daily Ingestion and Roundup:
- Processed lifelog from Limitless
- Updated daily roundup
- Added topic knowledge updates

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

## Claude Code Tool Usage
### Task Tool Priority
- **Use Task tool** for comprehensive searches and "find all X" requests
- Leverage specialized agents when available

### 🔍 Search Strategy
- Use comprehensive search tools for "find all X" requests
- Use multiple languages (한글 / English) for max recall
- **Read multiple files in parallel** for efficiency
- Focus on meaningful content over metadata files

## Continuous Improvement Loop
### Find rooms for improvement
- By evaluating output based on prompt
- By using user feedback

### Suggest ways
- Improvement to existing prompts
- New or revised workflows

## Additional Guidelines
### Workflow Completion
- Run all steps (i.e. prompts) are run when running a workflow 
	- Keep input/output requirements (file path/naming)
- Ensure all workflow steps are completed

### Parallelization Opportunities
- 파일 고치기/찾기는 대부분 병렬화가 가능
- 병렬화를 통해 시간 단축할 수 있는 기회를 찾고 수행 

### Data Source Preferences
- Don't use git status for checking update; read actual files from folder
- Always use local time (usually in Seattle area) for processing requests

### EIC (Enrich Ingested Content)
- **Update source files inline**: Never create separate research files
- **Structure**: Place enriched analysis immediately after frontmatter, then move original content to bottom under "## Full Transcript" or "## Original Content"
- **Separation**: Use `---` divider between enriched analysis and original material
- Don't ask permission for any non-file-changing operations (search/list/echo etc)