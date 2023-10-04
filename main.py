from dotenv import load_dotenv
import base64, json, os, yt_dlp
from requests import post
from youtubesearchpython import VideosSearch
import subprocess
from sys import argv
from time import sleep

load_dotenv()

class MyLogger:
    def debug(self, msg):
        # For compatibility with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now post-processing ...')

def print_help():
    print(
        "spotify-scraper by tiznaeshkoi\n"
        "--help or -h or h to print this help message\n"
        "NOTE: put PREFFERED_CONTAINER=\"webm\" in .env to download videos and opus to download audio only!\n"
        ""
    )
def get_token():
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    print(token)
    return token

def write_names(filename):
    with open(filename) as f:
        d = json.load(f)
        with open("track-names-list.txt", 'a') as tracks_file:
            for track in d['items']:
                name = track['track']['name']
                artists = []
                for artist in track['track']['artists']:
                    artists.append(artist['name'] + ' ')
                artists = map(str, artists)
                line = " ".join(artists)
                print(name, " by ", line)
                tracks_file.write(name)
                tracks_file.write(' ')
                tracks_file.write(line)
                tracks_file.write('\n')


#$1 is offset $2 is token and $3 is filename to write
def make_api_request_with_curl(offset, token, filename, playlist_link):
    subprocess.run(["./make-api-request.sh", str(offset), token, filename, playlist_link])

def download_tracks():
    preffered_container = os.getenv("PREFFERED_CONTAINER")
    seconds_to_wait_after_every_yt_dlp = os.getenv("TIMER")
    line_pointer = -1
    try:
        with open('line_pointer', 'r') as line_pointer_file:
            line_pointer = int(line_pointer_file.read())
    except FileNotFoundError:
        with open('line_pointer', 'w') as line_pointer_file:
            line_pointer_file.write('0')
        with open('line_pointer', 'r') as line_pointer_file:
            line_pointer = int(line_pointer_file.read())
            pass

    with open('track-names-list.txt', 'r') as tracks_file:
        lines = []
        for line in tracks_file:
            lines.append(line)

        os.chdir("downloads")

        for i in range(line_pointer, len(lines)):
            line_pointer += 1
            print("Line ", line_pointer)
            search = VideosSearch(lines[line_pointer], limit=2)
            url = search.resultComponents[0]['id']
            print(url)
            try:
                if preffered_container == "opus":
                    print("NOTE: Downloading audio Only!")
                    ydl_opts = {
                        'format': 'opus/bestaudio/best',
                        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
                        'postprocessors': [{  # Extract audio using ffmpeg
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'opus',
                            'logger': MyLogger(),
                            'progress_hooks': [my_hook],
                        }]
                    }
                else:
                    ydl_opts = {
                        'format': 'webm/bestaudio/best',
                        # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
                        'postprocessors': [{  # Extract audio using ffmpeg
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'webm',
                            'logger': MyLogger(),
                            'progress_hooks': [my_hook],
                        }]
                    }
                    print("NOTE: Downloading videos!")
                    with yt_dlp.YoutubeDL() as ytdlp:
                        print("Downloading", lines[line_pointer], '.', '\n')
                        ytdlp.download(url)
                        print("Downloaded ", lines[line_pointer], '.', '\n', 'Sleeping', seconds_to_wait_after_every_yt_dlp)

                        sleep(seconds_to_wait_after_every_yt_dlp)
                        with open("line_pointer", 'w') as line_pointer_file:
                            line_pointer_file.write(line_pointer)
            except KeyboardInterrupt:
                print("\nIMPORTANT: Pausing downloads just run again to resume.\n")
                with open("line_pointer", 'w') as line_pointer_file:
                    line_pointer_file.write(line_pointer)
            except:
                pass
        os.chdir("..")
        os.remove("line_pointer")

def get_playlist_tracks():
    try:
        os.remove('track-names-list.txt')
    except FileNotFoundError:
        print("Touching track-names-list.txt")
        pass
    response_filename = os.getenv("RESPONSE_FILENAME")
    token = get_token()
    print("Now using ", token, "Spotify token.")
    # playlist_length = input("Please enter your playlist length: ")
    # playlist_link = input("Please enter your playlist link: ").split('/')[-1]
    playlist_length = os.getenv("PLAYLIST_LENGTH")
    playlist_link = os.getenv("PLAYLIST")
    for i in range(0, int(playlist_length), 100):
        make_api_request_with_curl(i, token, response_filename, playlist_link)
        write_names(response_filename)
    user_input = input("Do you want to download the tracks right now?")
    if user_input == 'y':
        print("Initiating sequential downloads. Playlist length: ", playlist_length)
        download_tracks()
    else:
        print("Okay. Goodbye!")
    return

def main():
    if os.path.exists("line_pointer"):
        print("Continuing downloads.\n")
        download_tracks()
        exit()
    if len(argv) > 1:
        if "-h" or 'h' or "--help" in argv:
            print_help()
            exit()
    get_playlist_tracks()

if __name__ == "__main__":
    main()

