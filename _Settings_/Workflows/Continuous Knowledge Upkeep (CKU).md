## Overview
### Process
Run tasks for keeping knowledge base clean
(Run only if there's any updates in PKM since last update)
- Apply `EIC` for all newly ingested `Books`, `Articles` and `Clippings` notes
	- Don't process `Limitless` files
- Apply `UFN` for all folders with 1) updated notes and 2) existing folder notes
- Apply `TKI` for all updated `Topics` notes
Find ways to improve notes
- Fix broken links
- Add source attribution
### Guidelines
- Don't repeat job for files already processed
	- Use commit history / timestamp / contents to make judgments 

## Prompts
![[Enrich Ingested Content (EIC)]]

![[Update Folder Notes (UFN)]]

![[Topic Knowledge Improvement (TKI)]]
