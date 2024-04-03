from flask import Flask, render_template, request, redirect, flash
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from chat import promptgpt

#chat
app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set a secret key for session management

# Spotify authentication setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id='2a3cffe2f716412ebefe6e78a21157ab',
                                               client_secret='009ef54d5f9e403b89da9b4aa50e0d9b',
                                               redirect_uri='http://localhost:8080/callback',
                                               scope='playlist-modify-private'))

# Function to get playlist data
def get_playlist_data(query):
    results = sp.search(q=query, type='playlist')
    playlists = []
    for playlist in results['playlists']['items']:
        playlists.append({'name': playlist['name'], 'id': playlist['id']})
    return playlists

# Function to count song occurrences across all playlists
def count_songs_across_playlists(playlists):
    song_count = {}
    for playlist in playlists:
        playlist_id = playlist['id']
        tracks = sp.playlist_tracks(playlist_id)
        for item in tracks['items']:
            track = item.get('track')
            if track and track['id']:
                track_id = track['id']
                if track_id in song_count:
                    song_count[track_id]['count'] += 1
                else:
                    song_count[track_id] = {
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'count': 1,
                        'uri': track['uri']  # Include Spotify URI
                    }
    return sorted(song_count.values(), key=lambda x: x['count'], reverse=True)[:int(request.form['number'])]

# Function to create a playlist
def create_playlist(name, track_uris):
    user = sp.current_user()
    playlist = sp.user_playlist_create(user['id'], name, public=False)
    sp.playlist_add_items(playlist['id'], track_uris)
    return playlist['external_urls']['spotify']

@app.route('/')
def index():
    # Add your code to fetch top songs data here
    # For example:
    # top_songs = get_top_songs()
    top_songs = [...]  # Replace [...] with your top songs data
    return render_template('index.html', top_songs=top_songs)

@app.route('/create_playlist', methods=['POST'])
def create_playlist_route():
    playlist_name = request.form['playlist_name']  # Playlist name from form
    checked_song_uris = request.form.getlist('checked_songs')  # Get list of checked song IDs
    print("Checked song IDs:", checked_song_uris)  # Add logging to check the checked song IDs
    track_uris = []  # Initialize list to store URIs of checked songs
    # Split the string of URIs by comma and iterate over each URI
    for uri in checked_song_uris[0].split(','):
        # Remove any leading or trailing whitespace and append the URI to track_uris list
        track_uris.append(uri.strip())
    print("Track URIs:", track_uris)  # Add logging to check the track URIs
    if not track_uris:  # Check if list of track URIs is empty
        flash('Please select at least one song to create a playlist.', 'error')
        return redirect('/')

    # Create the playlist with checked songs
    playlist_url = create_playlist(playlist_name, track_uris)
    return redirect(playlist_url)

@app.route('/search', methods=['POST'])
def search():
    query = request.form['queryn']
    if query == "":
        query = promptgpt(request.form['queryd'])

    playlists = get_playlist_data(query)
    top_songs = count_songs_across_playlists(playlists)
    return render_template('top_songs.html', top_songs=top_songs)


if __name__ == '__main__':
    app.run(debug=True)
