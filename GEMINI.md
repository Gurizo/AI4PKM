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
- For files in AI Notes folder, omit "AI Notes/" prefix for brevity
- Example: `[[Roundup/2025-08-03 - AI Assistant]]` not `[[AI Notes/Roundup/2025-08-03 - AI Assistant]]`

### Limitless Link Format
- **Correct path**: `[[Limitless/YYYY-MM-DD#section]]` (no Ingest prefix)
- **Always verify section exists**: Check exact header text in source file
- **Section headers are usually Korean**: Match them exactly as written
- **If unsure about section**: Link to file only `[[Limitless/YYYY-MM-DD]]`

## 📁 File Management
- Create analysis files in `AI Notes/*/` folder unless instructed otherwise
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

## Gemini를 위한 규칙 (Lessons Learned)

*   **파일 경로 처리**: 파일 경로에 한글 또는 특수 문자가 포함되어 `read_many_files`가 실패할 경우, 개별 `read_file` 호출을 시도하여 파일 내용을 읽는다.
*   **파일 검색 시 `.gitignore` 고려**: 파일 목록을 찾거나 내용을 검색할 때, `.gitignore`에 의해 제외될 수 있는 경우 `respect_git_ignore=False` 옵션을 사용하여 모든 관련 파일을 포함한다.
*   **출력 파일명 및 경로 규칙 준수**: 사용자 요청에 따라 출력 파일명에 "by Gemini"를 포함하고, 지정된 하위 폴더(예: `AI Notes/Research`)에 저장한다.
*   **링크 형식 통일**: 출력 파일 내의 내부 링크는 위키링크(`[[파일명]]`) 형식을 사용한다.
*   **사용자 의도 명확화**: 사용자의 요청이 모호하거나, 특정 대상(예: AI 자신 vs. 사용자)에 대한 지시인지 불분명할 경우, 명확히 확인하여 혼동을 피한다.

