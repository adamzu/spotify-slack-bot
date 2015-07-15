#!/usr/bin/env osascript
on run {command, argument}
	launch application "Spotify"
	tell application "Spotify"
		if command is "current-song" then
			set theTrack to current track
			
			set theTrackArtist to artist of theTrack
			set theTrackName to name of theTrack
			set theTrackId to id of theTrack
			
			return theTrackId & "
" & theTrackName & "
" & theTrackArtist
		else if command is "playback-play" then
			play
		else if command is "playback-pause" then
			pause
		else if command is "playback-skip" then
			next track
		else if command is "playback-previous" then
			previous track
		else if command is "play-song" then
			play track argument
						set theTrack to current track
			
			set theTrackArtist to artist of theTrack
			set theTrackName to name of theTrack
			set theTrackId to id of theTrack
			return theTrackId & "
" & theTrackName & "
" & theTrackArtist
		end if
		
	end tell
	
end run