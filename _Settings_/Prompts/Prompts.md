---
tags: 
links: 
---
## Overview

## Recent Updates
%%auto-populated based on AI workflow%%

| Date | Title | Summary |
| ---- | ----- | ------- |
| 2025-08-14 | CKU Workflow Execution | Applied UFN process to update existing folder notes with recent knowledge activities |
| 2025-08-14 | [[Update Folder Notes (UFN)]] | Creates and updates folder notes with recent changes summaries |
| 2025-08-14 | [[Enrich Ingested Content (EIC)]] | Improves captured content structure, adds summaries, and enriches with topic links |
| 2025-08-14 | [[Weekly Journal Roundup (WJR)]] | Reviews weekly journals for goals, highlights, learnings, and next steps |
| 2025-08-11 | [[Generate Daily Roundup (GDR)]] | Creates daily roundups linking meaningful updates, topics, and enriches journal pages |
| 2025-08-10 | [[Process Life Logs (PLL)]] | Summarizes voice-based life logs with memorable items, emotions, and lessons |
| 2025-08-10 | [[(exp) Search and Discovery (SnD)]] | Discovers relevant content from web sources and creates research summaries |
| 2025-08-10 | [[Generate Weekly Roundup (GWR)]] | Generates weekly roundups highlighting key content from daily roundups |
| 2025-08-10 | [[Topic Knowledge Addendum (TKA)]] | Updates topic notes with new content from daily roundups |
| 2025-08-07 | [[Topic Knowledge Improvement (TKI)]] | Improves topic note structure, balance, and adds relevant sources |
| 2025-07-04 | [[Weekly Reading Review]] | Reviews weekly reading for learnings, topic applications, and next steps |

## List of All Notes
```dataviewjs
const title = dv.current().file.name;
const pages = dv.pages()
  .where(p => p.file.ext === "md"
           && p.file.path !== dv.current().file.path
           && p.file.folder.split("/").pop() === title);
dv.list(pages.sort(p => p.file.name, 'asc').map(p => p.file.link));
```
