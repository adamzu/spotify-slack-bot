from subprocess import check_output
from slackclient import SlackClient
import re
import time
import json
import threading
import requests
import signal
import sys
import private_settings as settings
import spotify

def _get_song_artists(song):
    song_artists = []
    num_artists = len(song.artists)
    for artist in song.artists:
        song_artists.append(artist.name)
    if num_artists == 2:
        song_artists = " and ".join(song_artists)
    else:
        song_artists = (", ".join(song_artists))[::-1].replace(", "[::-1], ", and "[::-1], 1)[::-1]
    return song_artists

def _get_song_data(song):
    return dict(song_id = str(song.link), song_name = song.name, song_artists = _get_song_artists(song))

def _get_recommendations(song_id):
    REQUEST_URL = "https://djlamp.herokuapp.com/api/recommend?id=%s" % song_id
    response = json.loads(requests.get(REQUEST_URL).content)
    recommendations = response["results"]
    return recommendations

class SpotifySlackBot():
    def __init__(self, api_key, broadcast_channel):
        self.broadcast_channel = broadcast_channel
        self.sc = SlackClient(api_key)
        self.session = spotify.Session()
        
        logged_in_event = threading.Event()
        def connection_state_listener(session):
            if session.connection.state is spotify.ConnectionState.LOGGED_IN:
                logged_in_event.set()
        
        loop = spotify.EventLoop(self.session)
        loop.start()
        self.session.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            connection_state_listener)
        self.session.login(settings.SPOTIFYUSERNAME, settings.SPOTIFYPASSWORD)
        logged_in_event.wait()
        loop.stop()
        
        # Get the user list
        response = self.sc.api_call('users.list')
        self.users = json.loads(response)['members']
        self.song_queue = []

    def command_current_song(self, event):
        data = self.run_spotify_script('current-song','')
        data = data.strip().split('\n')
        data = {"id": data[0], "name": data[1], "artist": data[2]}
        message = u"Hey, the current song is *%s* by *%s*. You can open it on Spotify: %s" % (data['name'], data['artist'], data['id'])
        
        self.sc.rtm_send_message(event['channel'], message)
        
    def command_playback_play(self, event):
        self.run_spotify_script('playback-play','')
        self.sc.rtm_send_message(event['channel'], "Sure, let the music play!")
        self.sc.rtm_send_message(self.broadcast_channel, "*Resumed playback*, as requested by %s." % (self.get_username(event['user'])))

    def command_playback_pause(self, event):
        self.run_spotify_script('playback-pause','')
        self.sc.rtm_send_message(event['channel'], "Alright, let's have some silence for now.")
        self.sc.rtm_send_message(self.broadcast_channel, "*Paused playback*, as requested by %s." % (self.get_username(event['user'])))

    def command_playback_skip(self, event):
        self.run_spotify_script('playback-skip','')
        self.sc.rtm_send_message(event['channel'], "Sure, let's listen to something else")
        self.sc.rtm_send_message(self.broadcast_channel, "*Skipping this song*, as requested by %s." % (self.get_username(event['user'])))

    def command_help(self, event):
        self.sc.rtm_send_message(event['channel'],
                                 "Hey, how are you?  I'm here to help you using our office playlist.\n"
                                 "I can give you some information about what is playing now and what will play afterwords, with the following commands:\n"
                                 "- `song` or `current`: I'll tell you which song is playing and who is the artist.\n"
                                 "- `queue`: I'll tell you all the songs in the queue.\n"
                                 "\n"
                                 "I can also control the playlist, with the following commands:\n"
                                 "- `play`: I'll resume playback of the playlist, if it is paused.\n"
                                 "- `pause`: I'll pause the playback of the playlist, if it is playing.\n"
                                 "- `queue SONG` or `play SONG` or : I'll search Spotify for a song that matches your SONG query and then add it to the song queue.\n"
                                 "- `skip` or `next`: I'll skip the current song and play another one.\n"
                                 "\n"
                                 "*Please note:* When you give commands to control the playlist, *I'll advertise on #%s that you asked me to do it*,"
                                 " just so everyone knows what is going on. Please use these only if you really need to :)"
                                    % (self.broadcast_channel)
        )

    def command_show_queue(self, event):
        message =  "*Song Queue:*\n"
        num_songs = len(self.song_queue)
        if not self.song_queue:
            message += "\tEMPTY"
        else:
            for number, (song, requester, requester_channel) in enumerate(self.song_queue):
                if(number > 9):
                    num_additional_songs = num_songs - number
                    message += "\t\t...%s more song" % num_additional_songs
                    if num_additional_songs > 1:
                        message += "s"
                    message += "..."
                    break
                song_data = _get_song_data(song)
                requester = self.get_username(requester)
                message += u"\t*%s*. *%s* by *%s* (%s) - requested by %s\n" % (number + 1, song_data['song_name'], song_data['song_artists'], song_data['song_id'], requester)
        self.sc.rtm_send_message(event['channel'], message)

    def command_queue_song(self, event):
        song_query = " ".join(event['text'].split()[1:])
        search = self.session.search(query=song_query)
        search.load()
        songs = search.tracks
        if not songs:
            self.sc.rtm_send_message(event['channel'], "Hey there! Sorry, I can't seem to find that song. Please try another.")
        else:
            position = len(self.song_queue) + 1
            song = songs[0]
            song_data = _get_song_data(song)
            requester = self.get_username(event['user'])
            message = u"%s added *%s* by *%s* (%s) to the song queue." % (requester, song_data['song_name'], song_data['song_artists'], song_data['song_id'])
            
            self.sc.rtm_send_message(event['channel'], "Sure, added *%s* by *%s* (%s) to the queue (*#%s*)." % (song_data['song_name'], song_data['song_artists'], song_data['song_id'], position))
            self.sc.rtm_send_message(self.broadcast_channel, message)
            self.song_queue.append((song, event['user'], event['channel']))

    def command_remove_from_queue(self, event):
        number = int(event['text'].split()[1])
        message = ""
        if number > len(self.song_queue):
            message = "Sorry, there is no song #*%s* on the queue. Type in a different number." % number
        else:
            index = number - 1
            (song, requester, requester_channel) = self.song_queue[index]
            song_data = _get_song_data(song)
            if event['user'] != requester:
                message = u"Sorry, you didn't request song #*%s*. *%s* by *%s*, so you can't remove it. Type in a different number." % (number, song_data['song_name'], song_data['song_artists'])
            else:
                self.song_queue.pop(index)
                message = u"Sure, I'll remove song #*%s*. *%s* by *%s* from the queue." % (number, song_data['song_name'], song_data['song_artists'])
                self.sc.rtm_send_message(self.broadcast_channel,
                                         u"%s removed song #*%s*. *%s* by *%s* from the queue." % (self.get_username(requester), number, song_data['song_name'], song_data['song_artists']))     
        self.sc.rtm_send_message(event['channel'], message)

    def play_next_song(self):
        if self.song_queue:
            (song, requester, requester_channel) = self.song_queue.pop(0)
            song_data = _get_song_data(song)
            requester = self.get_username(requester)
            message = u"Now playing *%s* by *%s* , as requested by %s. You can open it on Spotify: %s" % (song_data['song_name'], song_data['song_artists'], requester, song_data['song_id'])

            self.run_spotify_script('play-song', song_data['song_id'])
            self.sc.rtm_send_message(requester_channel, u"Now playing the song you requested: *%s* by *%s (%s)*!" % (song_data['song_name'], song_data['song_artists'], song_data['song_id']))
            self.sc.rtm_send_message(self.broadcast_channel, message)
        else:
            self.auto_queue()

    def auto_queue(self):
        print "EMPTY"

    def command_unknown(self, event):
        self.sc.rtm_send_message(event['channel'], "Hey there! I kinda didn't get what you mean, sorry. If you need, just say `help` and I can tell you how I can be of use. ;)")

    def run_spotify_script(self, *args):
        return check_output(['./spotify.applescript'] + list(args))

    def get_player_position(self):
        output = check_output(['./checkposition.applescript']).split("\n",1)
        output[0] = float(output[0]) / 1000
        output[1] = output[1].strip()
        return output

    def get_username(self, user_id):
        for user in self.users:
            if user['id'] == user_id:
                return '@%s' % user['name']
        return 'someone'
    
    def run(self):
        commands = [
            ('song|current', self.command_current_song),
            ('play$', self.command_playback_play),
            ('pause', self.command_playback_pause),
            ('skip|next', self.command_playback_skip),
            ('hey|help', self.command_help),
            ('queue$', self.command_show_queue),
            ('play .+|queue .+', self.command_queue_song),
            ('remove [1-9]([0-9])*', self.command_remove_from_queue),
            ('.+', self.command_unknown)
        ]
        
        if self.sc.rtm_connect():
            print("DJ Lamp is online!")
            self.sc.rtm_send_message(self.broadcast_channel, "<!channel>: DJ Lamp is now online and taking requests! Just send me a direct message (`hey` or `help` for help)!")
            while True:
                events = self.sc.rtm_read()
                for event in events:
                    print event
                    if event.get('type') == 'message' and event.get('channel')[0] == 'D':
                        for (expression, function) in commands:
                            if re.match(expression, event['text']):
                                function(event)
                                break
                position = self.get_player_position()
                print position
                if position == [0, 'paused']:
                    self.play_next_song()
                time.sleep(1)
        else:
            print("\rDJ Lamp aborted")
            sys.exit(0)

if __name__ == '__main__':
    print("DJ Lamp starting up...")
    try:
        bot = SpotifySlackBot(settings.SPOTIFYSLACK_SLACK_API_KEY, settings.SPOTIFYSLACK_SLACK_BROADCAST_CHANNEL)
    except KeyboardInterrupt:
        print("\rDJ Lamp aborted")
        sys.exit(0)
        
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\rDJ Lamp signing off!")
        bot.sc.rtm_send_message(bot.broadcast_channel, "<!channel>: DJ Lamp signing off! See ya next time!")
        sys.exit(0)