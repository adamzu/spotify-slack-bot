#!/usr/bin/env osascript
on run
	launch application "Spotify"
	tell application "Spotify"
		set repeating to false
		set shuffling to false
		return player position & "
" & player state as string
	end tell
end run
