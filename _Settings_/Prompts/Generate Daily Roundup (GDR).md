```
Target Date: YYYY-MM-DD (default: yesterday)
---
Generate daily roundup in AI/Roundup/{{YYYY-MM-DD}} Roundup - {{Agent-Name}}.md
1. Using Journal/{{YYYY-MM-DD}} as a starting point
	- Use [[Journal Template]] if the file doesn't exist
	- Keep the language (English/한글) of the original note 
	- Fill the sections of the note as follows
2. Link all meaningful note updates with summary
	- Apple Notes
	- Life Logs (AI/Lifelog)
	- Ingest (Articles / Clippings / Books)
3. Find and link related Topics
	- Format for links in header: "[[Page Title]]"
4. Enrich /Journal/{YYYY-MM-DD}.md page using this contents 
	- Be brief
	- Don't touch existing contents
	- Add link to roundup in `links` property
	- Each content should have link(s) to source note 
```
