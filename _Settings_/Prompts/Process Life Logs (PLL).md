```
Target Date: YYYY-MM-DD (default: yesterday)
---
Summarize voice-based life log in AI/Lifelog/{{YYYY-MM-DD}} Lifelog - {{Agent-Name}}.md
1. Using Ingest/Limitless/{{YYYY-MM-DD}} as a starting point
	- Keep the language (English/한글) of the original note 
	- Use [[Lifelog Template]] as a starting point
		- Respect the existing section structure
	- Chunk the file & merge if needed (don't omit any part)
	- Update the output file if the file exists
2. For each memorable log item
	- Memorable in terms of emotions felt / knowledge & info / lessons learned
		- Include key quotes in summary
		- Include conversation I highlighted (using == ==) 
		- Include memorable content from announcements, videos and music
	- Format it based on log type (monologue / chat / contents)
		- Add time of day & succinct title representing the whole topic
		- Add wiki links to original chat 
			- (Link: Limitless/{YYYY-MM-DD}#section)
			- Don't omit 'Limitless/' prefix 
	- If needed, add lessons / actions (in todo item)
		- If needed, wiki links relevant Topics and Readings
3. Add relevent photos from [[Pick and Process Photos (PPP)]] output
	- Match the timestamp btw. conversation and photo (use creation date metadata)
	- Add relevant photos to the story (Don't need to add all the photos)
	  - Ensure photos blend into the story naturally
```
