from twocaptcha import TwoCaptcha
from seleniumwire import webdriver
from seleniumwire.utils import decode
import music_tag
import argparse
import requests
import json
import os

# initalize parser
parser = argparse.ArgumentParser()

# add arguments
parser.add_argument("-s", "--Search", help="Search query")
parser.add_argument("-o", "--Output", help="Download location")
parser.add_argument("-c", "--Captcha", help="2Captcha Key")
parser.add_argument("-a", action="store_true", help="Search for album")
parser.add_argument("-t", action="store_true", help="Search for track")
parser.add_argument(
    "-l", action="store_true", help="Download lossless .flac (default is mp3)"
)

# read arguments
args = parser.parse_args()

# handle file_type arg
if args.l:
    file_type = "flac"
else:
    file_type = "mp3"

key = "k7xoeo5zc5osjouuaee4"
cookie = "6c541eg0fv112k8p0em17of3i4"

solver = TwoCaptcha(args.Captcha)
global_captcha = ""

# request headers
headers_dict = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "PHPSESSID=" + cookie + "; alertADSfree=yes; metaFLAC=yes; maybeErr=yes",
    "Host": "free-mp3-download.net",
    "Referer": "https://free-mp3-download.net/download.php?id=572554232&q=dGVzdCUyMGRyaXZl",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
    "Sec-Fetch-Dest": "iframe",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def download_track(trackId, album_id):
    # get album metadata from deezer
    album_req = requests.get("https://api.deezer.com/album/" + str(album_id))
    album = album_req.json()
    # find index of track in album
    for track in album["tracks"]["data"]:
        if track["id"] == trackId:
            track_index = album["tracks"]["data"].index(track)
    # download request params
    download_req_params = {
        "i": album["tracks"]["data"][track_index]["id"],
        "ch": key,
        "f": file_type,
        "h": global_captcha,
    }
    # start download
    download_req = requests.get(
        "https://free-mp3-download.net/dl.php",
        download_req_params,
        headers=headers_dict,
    )
    artist_name = album["artist"]["name"]
    album_name = album["title"]
    track_name = album["tracks"]["data"][track_index]["title"]
    # apply formatting for tags
    track_index += 1
    if track_index < 10:
        track_index = str(0) + str(track_index)
    # handle output folder arg
    if args.Output:
        folder = args.Output + "/" + artist_name + " - " + album_name
    else:
        folder = artist_name + " - " + album_name
    # create album folder
    if not os.path.exists(folder):
        os.makedirs(folder)
    # write data to file
    with open(
        folder + "/" + str(track_index) + " - " +
        track_name + "." + file_type, "wb"
    ) as f:
        f.write(download_req.content)
    print(str(track_index) + " - " + track_name + "." + file_type)
    # set track metadata
    local_track = music_tag.load_file(
        folder + "/" + str(track_index) + " - " + track_name + "." + file_type
    )
    local_track["tracktitle"] = track_name
    local_track["album artist"] = artist_name
    local_track["album"] = album_name
    local_track["trackNumber"] = track_index
    local_track["year"] = album["release_date"][0:4]
    # set artwork
    with open("cover.jpg", "rb") as img_in:
        local_track["artwork"] = img_in.read()
    with open("cover.jpg", "rb") as img_in:
        local_track.append_tag("artwork", img_in.read())
    local_track.save()


def get_artwork(album_data):
    cover_art_req = requests.get(
        album_data["data"][0]["album"]["cover_xl"])
    with open("cover.jpg", "wb") as f:
        f.write(cover_art_req.content)


def album():
    # get deezer album data
    search_req_params = {"q": 'album:"' + args.Search + '"'}
    search_req = requests.get(
        "https://api.deezer.com/search", search_req_params)
    data = search_req.json()
    album_id = data["data"][0]["album"]["id"]
    print("album found: " + str(album_id))
    get_artwork(data)
    album_req = requests.get("https://api.deezer.com/album/" + str(album_id))
    data = album_req.json()
    # download tracks
    for track in data["tracks"]["data"]:
        download_track(track["id"], data["id"])
    # delete artwork file
    os.remove("cover.jpg")


def track():
    # get deezer track data
    search_req = requests.get("https://api.deezer.com/search?q=" + args.Search)
    data = search_req.json()
    get_artwork(data)
    download_track(data["data"][0]["id"], data["data"][0]["album"]["id"])
    # delete artwork file
    os.remove("cover.jpg")


def solve_captcha():
    print("solving captcha")
    captcha = solver.recaptcha(
        sitekey="6LfzIW4UAAAAAM_JBVmQuuOAw4QEA1MfXVZuiO2A",
        url="http://free-mp3-download.net/",
    )
    with open("captcha.json", "w") as stored_captcha:
        captcha = str(captcha).replace("'", '"')
        stored_captcha.write(captcha)
    captcha = json.loads(captcha)["code"]
    validate_captcha()
    print("captcha solved")
    return captcha


def validate_captcha():
    # download request params
    download_req_params = {"i": 572554232, "ch": key,
                           "f": file_type, "h": global_captcha}
    # download request
    download_req = requests.get(
        "https://free-mp3-download.net/dl.php",
        download_req_params,
        headers=headers_dict,
    )
    if download_req.text == "Incorrect captcha":
        print("ERROR")
        exit()


def prompt_captcha():
    driver = webdriver.Chrome()
    # create a request interceptor

    def interceptor(request):
        # replacee referer header
        del request.headers['Referer']
        request.headers['Referer'] = 'https://free-mp3-download.net/'
    # set request interceptor
    driver.request_interceptor = interceptor
    driver.get(
        'https://free-mp3-download.net/download.php?id=572554232&q=dGVzdCUyMGRyaXZl')
    # show only captcha box
    driver.execute_script(
        "var saved = document.getElementById('captcha'); var elms = document.body.childNodes; while (elms.length) elms[0].parentNode.removeChild(elms[0]); document.body.appendChild(saved);")
    # set window to smallest size
    driver.set_window_size(1, 625)
    # search for captcha response
    found = False
    while found == False:
        try:
            for request in driver.requests:
                if request.response:
                    if "https://www.google.com/recaptcha/api2/userverify" in request.url:
                        found = True
                        # parse captcha token
                        captcha = decode(request.response.body, request.response.headers.get(
                            'Content-Encoding', 'identity'))
                        captcha = json.loads(captcha[5:].decode('utf-8'))[1]
                        print(len(captcha))
                        if len(captcha) > 600:
                            continue
                        print("grabbed captcha")
                        with open("captcha.json", "w") as stored_captcha:
                            stored_captcha.write(
                                '{"captchaId": "", "code": "' + captcha + '"}')
                        return captcha
        except:
            continue


def handle_captcha():
    if args.Captcha == None:
        return (prompt_captcha())
    else:
        return (solve_captcha())


def check_stored_captcha():
    # validate stored captcha
    if os.path.exists("captcha.json"):
        stored_captcha = open("captcha.json", "r")
        global_captcha = stored_captcha.read()
        global_captcha = json.loads(global_captcha)["code"]
        stored_captcha.close()
        # test stored captcha
        print("testing stored captcha")
        # download request params
        download_req_params = {"i": 572554232,
                               "ch": key, "f": "mp3", "h": global_captcha}
        # download request
        download_req = requests.get(
            "https://free-mp3-download.net/dl.php",
            download_req_params,
            headers=headers_dict,
        )
        if download_req.text == "Incorrect captcha":
            global_captcha = handle_captcha()
        else:
            print("stored captcha is valid")
    else:
        global_captcha = handle_captcha()


check_stored_captcha()

# handle download type arg
if args.a:
    album()
if args.t:
    track()
