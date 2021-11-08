from twocaptcha import TwoCaptcha
import music_tag
import argparse
import requests
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

# handle filetype arg
if args.l:
    fileType = "flac"
else:
    fileType = "mp3"

key = "k7xoeo5zc5osjouuaee4"
cookie = "6c541eg0fv112k8p0em17of3i4"

solver = TwoCaptcha(args.Captcha)

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


def downloadTrack(trackId, albumId):
    # get album metadata from deezer
    albumReq = requests.get("https://api.deezer.com/album/" + str(albumId))
    album = albumReq.json()
    # find index of track in album
    for track in album["tracks"]["data"]:
        if track["id"] == trackId:
            trackIndex = album["tracks"]["data"].index(track)
    # download request params
    downloadReqParams = {
        "i": album["tracks"]["data"][trackIndex]["id"],
        "ch": key,
        "f": fileType,
        "h": captcha,
    }
    # start download
    downloadReq = requests.get(
        "https://free-mp3-download.net/dl.php",
        downloadReqParams,
        headers=headers_dict,
    )
    artistName = album["artist"]["name"]
    albumName = album["title"]
    trackName = album["tracks"]["data"][trackIndex]["title"]
    # apply formatting for tags
    trackIndex += 1
    if trackIndex < 10:
        trackIndex = str(0) + str(trackIndex)
    # handle output folder arg
    if args.Output:
        folder = args.Output + "/" + artistName + " - " + albumName
    else:
        folder = artistName + " - " + albumName
    # create album folder
    if not os.path.exists(folder):
        os.makedirs(folder)
    # write data to file
    with open(
        folder + "/" + str(trackIndex) + " - " +
        trackName + "." + fileType, "wb"
    ) as f:
        f.write(downloadReq.content)
    print(str(trackIndex) + " - " + trackName + "." + fileType)
    # set track metadata
    localTrack = music_tag.load_file(
        folder + "/" + str(trackIndex) + " - " + trackName + "." + fileType
    )
    localTrack["tracktitle"] = trackName
    localTrack["album artist"] = artistName
    localTrack["album"] = albumName
    localTrack["trackNumber"] = trackIndex
    localTrack["year"] = album["release_date"][0:4]
    # set artwork
    with open("cover.jpg", "rb") as img_in:
        localTrack["artwork"] = img_in.read()
    with open("cover.jpg", "rb") as img_in:
        localTrack.append_tag("artwork", img_in.read())
    localTrack.save()


def getArtwork(albumData):
    coverArtReq = requests.get(
        albumData["data"][0]["album"]["cover_xl"])
    with open("cover.jpg", "wb") as f:
        f.write(coverArtReq.content)


def album():
    # get deezer album data
    searchReqParams = {"q": 'album:"' + args.Search + '"'}
    searchReq = requests.get("https://api.deezer.com/search", searchReqParams)
    data = searchReq.json()
    albumId = data["data"][0]["album"]["id"]
    print("album found: " + str(albumId))
    getArtwork(data)
    albumReq = requests.get("https://api.deezer.com/album/" + str(albumId))
    data = albumReq.json()
    # download tracks
    for track in data["tracks"]["data"]:
        downloadTrack(track["id"], data["id"])
    # delete artwork file
    os.remove("cover.jpg")


def track():
    # get deezer track data
    searchReq = requests.get("https://api.deezer.com/search?q=" + args.Search)
    data = searchReq.json()
    getArtwork(data)
    downloadTrack(data["data"][0]["id"], data["data"][0]["album"]["id"])
    # delete artwork file
    os.remove("cover.jpg")


def solveCaptcha():
    print("solving captcha")
    captcha = solver.recaptcha(
        sitekey="6LfzIW4UAAAAAM_JBVmQuuOAw4QEA1MfXVZuiO2A",
        url="http://free-mp3-download.net/",
    )
    with open("captcha.json", "w") as storedCaptcha:
        captcha = str(captcha).replace("'", '"')
        storedCaptcha.write(captcha)
    captcha = captcha[1]
    print("captcha solved")


def validateKey(captcha):
    # download request params
    reqParams = {"i": 572554232, "ch": key, "f": fileType, "h": captcha}
    # download request
    req = requests.get(
        "https://free-mp3-download.net/dl.php",
        reqParams,
        headers=headers_dict,
    )


# validate stored captcha
if os.path.exists("captcha.json"):
    storedCaptcha = open("captcha.json", "r")
    captcha = storedCaptcha.read()
    captcha = captcha[1]
    storedCaptcha.close()
    # test stored captcha
    print("testing stored captcha")
    validateKey(captcha)
    # download request params
    downloadReqParams = {"i": 572554232, "ch": key, "f": "mp3", "h": captcha}
    # download request
    downloadReq = requests.get(
        "https://free-mp3-download.net/dl.php",
        downloadReqParams,
        headers=headers_dict,
    )
    if downloadReq.text == "Incorrect captcha":
        solveCaptcha()
    else:
        print("stored captcha is valid")
else:
    solveCaptcha()

# handle download type arg
if args.a:
    album()
if args.t:
    track()
