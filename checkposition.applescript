#!/usr/bin/env osascript
on run
	launch application "Spotify"
	tell application "Spotify"
		return player position
	end tell
end run
