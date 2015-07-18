# Spotify-Slack-Bot Mk. II - DJ Lamp!
(forked from https://github.com/Cisneiros/spotify-slack-bot)

*Bring life to your office with a collaboratively controlled Spotify session via Slack!*

DJ Lamp is a Slack bot that controls an instance of Spotify on a particular computer. It can tell what song is playing, control playback (e.g. playing and pausing), play and queue song requests, and even pick its own songs to play based on the last song that played, if there are no queued requests. Run it on a machine with Spotify installed, connect it to your office speakers, and you and your whole office now have your very own personal Slack Bot DJ. Now, everyone at the office can collaboratively play nice music for the whole office to hear without needing physical access to the computer running Spotify. 

## Features

* Song Info: Tells anyone the name, artist, and Spotify URI of a song playing via Private Message (so as to not disturb anyone else).
* Controls playback: play, pause and skip a song.
* Song requests: play any song on Spotify with a simple query.
* Song queueing: add or remove songs from a queue to determine which songs will be played.
* DJ mode: will automatically pick and play songs based on the last played song when the queue is empty
* Channel Broadcast: Informs the whole channel when DJ Lamp goes online or offline, someone plays or pauses playback, requests a song or removes it from the queue, etc.

## What you need

* A computer (Mac OS X only, for now) running Spotify (make sure it's Spotify version 1.0.9 or higher).
* Python and Ruby (already included with OS X), `pip`, and `brew`.
* A Slack Bot integration setup and its API Key.
* A Slack channel dedicated to your playlist for the bot to broadcast messages when needed.
* A Spotify Premium Account (you can't get a Spotify Developer Account without a non-Premium account)
* A Spotify application key

## Installing

If you don't have `pip`, you can get it with:

```shell
sudo easy_install pip
```

If you don't have `brew`, you can get it with:

```shell
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

Clone the repository on your machine and then install the dependencies from the cloned repository's root folder.

```shell
brew install mopidy/mopidy/libspotify
xcode-select --install
sudo pip install -r requirements.txt
```

## Configuring and Running

First, you'll need to create a Slack Bot integration. Go to https://slack.com/integrations, select "Bots", and then add a new Bot. Call it whatever you like; we suggest djlamp :). Then copy its API Token. You'll need it for later.

Next, you'll need a Spotify application key. Again, you can only get one if you have a Spotify Premium account, so be sure to upgrade! Go to https://devaccount.spotify.com/my-account/keys and make a new app. Make a new application and then download the Binary Key (the C-Code one won't work) and move it to the cloned repository's root folder. 

Then, you'll need to get your device username and set up a device password for the computer you will run DJ Lamp from. Go to https://www.spotify.com/us/account/set-device-password/ and click "Send Email To Set Password." Copy the username and save it for later. Use the link in the email message to create a new password. It DOES NOT have to be the same as your Spotify account password, and we recommend that you choose a different one as this password will be visible in a settings file on your computer. Copy the password and save it for later as well.

Finally, You'll need to create a file called `private_settings.py` in the root folder of the cloned repository in the following format:

* `SPOTIFYSLACK_SLACK_API_KEY = #your Bot integration API Key#`
* `SPOTIFYSLACK_SLACK_BROADCAST_CHANNEL = #the Channel ID for your broadcast channel#`
* `SPOTIFY_USERNAME = #your Spotify app username#`
* `SPOTIFY_PASSWORD = #your Spotify app password#`

You should now be good to go! Open Terminal, navigate to the root folder of the cloned repository, and run the following:

```shell
python djlamp.py
```

Be sure to terminate DJ Lamp with `ctrl-c` when you're done, so people can't control your music when you don't want to! Also don't close Spotify while DJ Lamp is running! It immediately makes the entire world's puppy population start weeping. Seriously...

## Why OS X only?

The bot uses AppleScript to talk to the Spotify client running on the computer. The name kinda makes it obvious it is not supported on non-Apple operating systems. There might be ways to control and get data from the player on Windows and Linux, but for now it's just Mac OS X.

## Final Comments

DJ mode uses a song recommendation system created by Andrew Violino's (aviolino) djlamp feature (https://github.com/aviolino/djlamp). Thanks to him for providing the feature!

Again, this is a fork from Alexandre Cisneiros' (Cisneiros) Spotify-Slack-Bot (https://github.com/Cisneiros/spotify-slack-bot). Thanks to him for creating a great project! Below is his original license, followed by our license:

## Original License: MIT

Copyright © 2015 Alexandre Cisneiros - www.cisneiros.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## DJ Lamp License: MIT

Copyright © 2015 Adam Zucker

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
