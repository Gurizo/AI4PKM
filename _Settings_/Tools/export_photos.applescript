set albumName to "AI4PKM"

-- Create folder and resolve absolute path
set destPOSIX to (do shell script "mkdir -p ./Photostream && cd ./Photostream && pwd")

tell application "Photos"
	
	-- Get existing files in destination (base names without extensions)
	try
		set existingFiles to do shell script "ls " & quoted form of destPOSIX & " | sed 's/\\.[^.]*$//' | sort -u"
	on error
		set existingFiles to ""
	end try
	
	set allItemsToExport to {}
	
	-- Find the album
	set albs to (every album whose name is albumName)
	if (count of albs) > 0 then
		set a to item 1 of albs
		set allItems to media items of a
		
		-- Loop through every photo in the album
		repeat with anItem in allItems
			-- Skip if it's a movie (so Live Photos won’t export the .mov part)
			if (class of anItem as string) is not "movie" then
				set itemFilename to filename of anItem
				-- Remove extension
				set baseName to my removeExtension(itemFilename)
				
				-- Only export if not already present
				if existingFiles does not contain baseName then
					set end of allItemsToExport to anItem
				end if
			end if
		end repeat
	end if
	
	-- Export new items (images only)
	if (count of allItemsToExport) > 0 then
		export allItemsToExport to (POSIX file destPOSIX as alias) with using originals
	end if
end tell

-- Helper function: remove extension
on removeExtension(fileName)
	set AppleScript's text item delimiters to "."
	set nameComponents to text items of fileName
	set AppleScript's text item delimiters to ""
	if (count of nameComponents) > 1 then
		set nameComponents to items 1 thru -2 of nameComponents
		set AppleScript's text item delimiters to "."
		set baseName to nameComponents as string
		set AppleScript's text item delimiters to ""
		return baseName
	else
		return fileName
	end if
end removeExtension