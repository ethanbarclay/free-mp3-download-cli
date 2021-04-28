# free-mp3-cli

script for downloading full albums and tracks as mp3 or flac from http://free-mp3-download.net/

# how to use

1. `pip install -r requirements.txt`
2. `python main.py -a -s <search query> -o <output folder location>`

# options

```
  -h, --help            Show help message and exit
  -s SEARCH, --Search SEARCH
                        Search query
  -o OUTPUT, --Output OUTPUT
                        Download location
  -a, --Album           Search for album
  -t, --Track           Search for track
  -l, --Lossless        Download lossless .flac (default is mp3)
```
