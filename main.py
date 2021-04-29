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

key = "3yr22yg1hgr4pnm57yzb04"
cookie = "d50jg47j8lq1engmm7ba3s1cg0"


def downloadTrack(trackId, albumId):
    # find albumId by requesting track info
    if albumId is None:
        trackReq = requests.get("https://api.deezer.com/track/" + str(trackId))
        track = albumReq.json()
        albumId = track["album"]["id"]

    # get album metadata from deezer
    albumReq = requests.get("https://api.deezer.com/album/" + str(albumId))
    album = albumReq.json()

    # find index of track in album
    for track in album["tracks"]["data"]:
        if track["id"] == trackId:
            trackIndex = album["tracks"]["data"].index(track)

    # download request params
    albumDownloadParams = {
        "i": album["tracks"]["data"][trackIndex]["id"],
        "ch": key,
        "f": fileType,
    }
    headers_dict = {
        "Host": "free-mp3-download.net",
        "Connection": "keep-alive",
        "sec-ch-ua": '"Chromium";v="91", " Not;A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4467.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "iframe",
        "Referer": "https://free-mp3-download.net/download.php?id=713829",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Cookie": "PHPSESSID=" + cookie + "; alertADSfree=yes",
    }

    # start download
    albumDownload = requests.get(
        "https://free-mp3-download.net/dl.php",
        albumDownloadParams,
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
        folder + "/" + str(trackIndex) + " - " + trackName + "." + fileType, "wb"
    ) as f:
        f.write(albumDownload.content)

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


def album():
    searchReqParams = {"q": args.Search}
    searchReq = requests.get("https://api.deezer.com/search", searchReqParams)

    # get deezer album id
    data = searchReq.json()
    albumId = data["data"][0]["album"]["id"]
    print("Album Id: " + str(albumId))

    # download cover art
    coverArtReq = requests.get(data["data"][0]["album"]["cover_xl"], searchReqParams)
    with open("cover.jpg", "wb") as f:
        f.write(coverArtReq.content)

    albumReq = requests.get("https://api.deezer.com/album/" + str(albumId))
    data = albumReq.json()

    for track in data["tracks"]["data"]:
        downloadTrack(track["id"], data["id"])


def track():
    searchReq = requests.get("https://api.deezer.com/search?q=" + args.Search)
    data = searchReq.json()
    downloadTrack(data["data"][0]["id"], data["data"][0]["album"]["id"])


# handle download type arg
if args.a:
    album()
if args.t:
    track()
