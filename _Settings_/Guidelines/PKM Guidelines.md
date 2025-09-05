## Overview
### Definitions
- PKM[^1] : the whole practice of managing personal information and knowledge
- (P)KB[^2] / Repo / Vault : information and knowledge stored in a PKM system
## Guiding Principles
### PKM is for both Human and AI
This guideline is meant for both human user and AI assistants / agents
- AI-created contents are kept separately from human-written notes
- Notes that can be modified by both human and AI are put in VCS for safety
### Tool-agnostic Approach
Assume that multiple tools can and will process the contents of PKM. As of Aug. 2025, the following application are used, each with different purposes:
- `Obsidian` is used as a main front-end for human user 
	- Primarily as a markdown editor that can manage cross-note links[^3]
- `Cursor` is used as a tool for human-AI collaborative editing
- `Claude Code` is used for agentic processing of PKM prompts and workflows
### Accommodate Multiple AI Tools
Need to constantly experiment with multiple AI tools and models
- For that reason, AI-created contents should have clear label on who created it & why

## PKM Overview
1. Contents are ingested from various sources, and then get processed for quality (e.g. remove transcription error) and richness. 
2. Processed contents are then indexed by topic and time period (day/week) that constitute 
3. Contents in KB are then used in various `Projects` or shared in messages and social media. 

![[PKM Guidelines 2025-07-20 09.43.31.excalidraw.svg]]
%%[[PKM Guidelines 2025-07-20 09.43.31.excalidraw.md|🖋 Edit in Excalidraw]]%%

## PKM Workflows
AI is used extensively for my PKM practices. These workflows ensure my KB is kept up-to-date.
- [[Daily Ingestion and Roundup (DIR)]]
- [[Weekly Roundup and Planning (WRP)]]
- [[Continuous Knowledge Upkeep (CKU)]]

![[PKM Guidelines 2025-08-14 12.13.54.excalidraw.svg]]
%%[[PKM Guidelines 2025-08-14 12.13.54.excalidraw.md|🖋 Edit in Excalidraw]]%%

The following prompts and templates are extensively used within workflows to represent individual step and input/output notes.
- `_Settings_/Prompts`
- `_Settings_/Templates`

## PKM Applications
PKM supports following applications
### Ad-hoc Rsesarch
![[(exp) Ad-hoc Research within PKM (ARP)]]

### Contents Creation
![[PKM in AI Era (slides) 2025-08-18 11.25.13.excalidraw.svg]]
![[Create Thread Postings (CTP)]]
## Appendix
### Properties
[[Default Template]] contains default properties.
 - Links : add list of linked notes
 - Tags : add list of tags

```
---
tags: 
links: 
---
```

### Tags
Tag complements main (hierarchical) organization.

Common tags include:
- Tasks
	- #TODO #TOREAD #followup 
- Topics
	- #PKM
- Anything else

[^1]: Personal Knowledge Management
[^2]: (Personal) Knowledge Base
[^3]: And show pretty graphs of KB contents
