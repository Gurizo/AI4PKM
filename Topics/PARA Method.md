---
aliases: 
  - PARA
tags: 
  - para-method
related: 
  - "[[Topics/Second Brain]]"
---
## Summary

PARA is a simple, comprehensive, yet extremely flexible system for organizing any type of digital information across any platform. It stands for Projects, Areas, Resources, and Archive. ([[Ingest/Clippings/2025-09-09 Building a Second Brain The Definitive Introductory Guide.md|Building a Second Brain: The Definitive Introductory Guide]])

## Interests

- How to use the PARA method to organize my digital life.

## Experiences

- None

## Learnings

- **Projects:** short-term efforts (in your work or personal life) that you take on with a certain goal in mind
- **Areas:** Long-term responsibilities you want to manage over time
- **Resources:** Topics or interests that may be useful in the future
- **Archive:** Inactive items from the other 3 categories

All from [[Ingest/Clippings/2025-09-09 Building a Second Brain The Definitive Introductory Guide.md|Building a Second Brain: The Definitive Introductory Guide]]

## See Also

- [[Topics/Second Brain]]
- [[Topics/CODE Methodology]]

```dataview
TABLE file.mtime AS "Updated", file.size AS "Size" 
WHERE startswith(file.folder, this.file.folder) 
      AND file.name != this.file.name  
```
