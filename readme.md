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
  -c CAPTCHA, --Captcha CAPTCHA
                        2Captcha Key
  -a                    Search for album
  -t                    Search for track
  -l                    Download lossless .flac (default is mp3)
```
