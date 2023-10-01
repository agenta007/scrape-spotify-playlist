from dotenv import load_dotenv
import base64, json, os, yt_dlp
from requests import post
from youtubesearchpython import VideosSearch
import subprocess

from youtube_search import YoutubeSearch

load_dotenv()
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
                print(name)
                tracks_file.write(name)
                tracks_file.write('\n')


#$1 is offset $2 is token and $3 is filename to write
def make_api_request_with_curl(offset, token, filename, playlist_link):
    #os.system(f"./make-api-request.sh {offset} {token} {filename} {playlist_link}")
    subprocess.run(["./make-api-request.sh", str(offset), token, filename, playlist_link])

def download_tracks():
    with open('track-names-list.txt', 'r') as tracks_file:
        for line in tracks_file:
            #results = YoutubeSearch(line , max_results=1).to_dict()
            search = VideosSearch(line, limit=2)
            #url = str.removeprefix(results[0]['url_suffix'], "/watch?v=")
            url = search.resultComponents[0]['id']

            print(url)
            try:
                with yt_dlp.YoutubeDL() as ytdlp:
                    ytdlp.download(url)
            except:
                pass

def main():

    download_tracks()
    exit()
    response_filename = os.getenv("RESPONSE_FILENAME")
    token = get_token()
    #playlist_length = input("Please enter your playlist length: ")
    #playlist_link = input("Please enter your playlist link: ").split('/')[-1]
    playlist_length = 1946
    playlist_link = '0D23BVWbwdJU74NsmQpGly'
    for i in range(0, int(playlist_length), 100):
        make_api_request_with_curl(i, token, response_filename, playlist_link)
        write_names(response_filename)

if __name__ == "__main__":
    main()

