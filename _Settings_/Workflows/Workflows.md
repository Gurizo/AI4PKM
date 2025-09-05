---
aliases: 
tags: 
related: 
---
## Overview
These are workflows for Obsidian repo 
- App paths are within $OV2024 env var

## Recent Updates
%%auto-populated based on AI workflow%%

| Date | Title | Summary |
| ---- | ----- | ------- |
| 2025-08-14 | [[Continuous Knowledge Upkeep (CKU)]] | Workflow for maintaining knowledge base with EIC, TKI, and UFN processes |
| 2025-08-13 | PLL→GDR→ATN Workflow | Executed comprehensive daily workflow: Process Limitless Log → Generate Daily Roundup → Add Topic Knowledge |
| 2025-08-13 | Knowledge Integration | Systematic integration of AI era essays into topic knowledge base |

### Triggered Workflows


%% 
#### Process Lifelog
Trigger:
- File change in `Ingest/Limitless`
Action:
- Call OpenAI API with params below:
	- Prompt: PRL 
	  in `obsidian://open?vault=OV2024&file=_Settings_%2FPrompts%2FProcess%20Lifelogs%20(PRL)`
	- Model: gpt-4o
	- Date: extract from file that changed
Success Criteria: 
- Processed output in `AI/Lifelog`
- Model name added to file suffix %%
### Daily Workflows
