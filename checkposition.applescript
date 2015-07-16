#!/usr/bin/env osascript
on run
	launch application "Spotify"
	tell application "Spotify"
		return player position & "\n" & player state as string
	end tell
end run
